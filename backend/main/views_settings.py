import asyncio
import json
import os
import shutil
from datetime import date
from io import BytesIO
from pathlib import Path

import litellm
import pandas
import plotly.graph_objects as go
import plotly.io as pio
from langchain.agents import create_agent
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from PIL import Image
from django.contrib import messages
from django.http import JsonResponse, FileResponse, StreamingHttpResponse

from backend.main import settings
from backend.main.views_helper import sanitize_name, load_settings_from_file
from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH, SETTINGS_PATH
from backend.protzilla.data_integration.database_query import (
    uniprot_columns,
    uniprot_databases,
)
from backend.protzilla.disk_operator import YamlOperator
from backend.main.views_helper import load_yaml_from_file
from backend.protzilla.constants.paths import (
    CUSTOM_AI_SETTINGS_FILE_STEM,
    CUSTOM_PLOT_SETTINGS_FILE_STEM,
    DEFAULT_AI_SETTINGS_FILE_STEM,
    DEFAULT_PLOT_SETTINGS_FILE_STEM,
    DEFAULT_PTM_SETTINGS_FILE_STEM,
    CUSTOM_PTM_SETTINGS_FILE_STEM,
    DATABASE_METADATA_PATH,
    MCP_SERVER_PATH,
)

def _litellm_value(value):
    return getattr(value, "value", str(value))


def _chat_message_content(message):
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    if content is None:
        return ""
    return str(content)


def _jsonable_chat_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable_chat_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable_chat_value(item) for key, item in value.items()}
    if hasattr(value, "model_dump"):
        return _jsonable_chat_value(value.model_dump())
    return str(value)


async def _stream_chat_message_with_langchain(
    model: str, api_key: str, messages: list[dict]
):
    if not MCP_SERVER_PATH.exists():
        raise ValueError(
            f"MCP server file not found at '{MCP_SERVER_PATH}'. Recreate the django container so the mcp-server volume is mounted."
        )

    client = MultiServerMCPClient(
        {
            "protzilla": {
                "transport": "stdio",
                "command": "python",
                "args": [str(MCP_SERVER_PATH)],
            }
        }
    )
    tools = await client.get_tools()
    agent = create_agent(
        model=ChatLiteLLM(model=model, api_key=api_key),
        tools=tools,
        system_prompt=(
            "You are PROTzilla's AI assistant. Use PROTzilla tools whenever they "
            "help. Many PROTzilla tools already contain detailed descriptions of "
            "their expected inputs, return values, constraints, and behaviour, so "
            "read those tool descriptions carefully before acting. Prefer the "
            "information from PROTzilla tools over guessing. If documentation is "
            "needed, the PROTzilla wiki lives at "
            "https://github.com/cschlaffner/PROTzilla/wiki."
        ),
    )
    async for chunk in agent.astream(
        {"messages": messages}, stream_mode="updates", version="v2"
    ):
        if chunk.get("type") != "updates":
            continue

        for node_data in chunk.get("data", {}).values():
            for message in node_data.get("messages", []):
                tool_calls = getattr(message, "tool_calls", None)
                if tool_calls:
                    for tool_call in tool_calls:
                        yield {
                            "type": "tool_start",
                            "tool_call_id": (
                                tool_call.get("id")
                                if isinstance(tool_call, dict)
                                else getattr(tool_call, "id", None)
                            ),
                            "tool": (
                                tool_call.get("name")
                                if isinstance(tool_call, dict)
                                else getattr(tool_call, "name", "")
                            ),
                            "arguments": _jsonable_chat_value(
                                tool_call.get("args")
                                if isinstance(tool_call, dict)
                                else getattr(tool_call, "args", {})
                            ),
                        }
                    continue

                if getattr(message, "type", None) == "tool":
                    yield {
                        "type": "tool_result",
                        "tool_call_id": getattr(message, "tool_call_id", None),
                        "result": _jsonable_chat_value(
                            getattr(message, "content", None)
                        ),
                    }
                    continue

                answer = _chat_message_content(message)
                if answer:
                    yield {"type": "answer", "answer": answer}


def load_settings(request, default_file_stem: str):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON response while loading the settings.",
                },
                status=400,
            )
        template_name = data.get("templateName")

        settings = load_settings_from_file(template_name, default_file_stem)
        return JsonResponse(settings)
    return JsonResponse(
        {"success": False, "message": "Only POST requests are allowed."}, status=405
    )


# <--- Plot Export --->


def load_plot_settings(
    request, default_file_stem: str = DEFAULT_PLOT_SETTINGS_FILE_STEM
):
    return load_settings(request, default_file_stem)


def save_plot_settings(request):
    if request.method == "POST":
        settings = json.loads(request.body.decode("utf-8"))
        op = YamlOperator()
        path = SETTINGS_PATH / f"{CUSTOM_PLOT_SETTINGS_FILE_STEM}.yaml"
        try:
            op.write(path, settings)
        except:
            return JsonResponse(
                {"success": False, "message": "Saving failed!"}, status=400
            )

        # TODO Update Plotly template that is used in run screen
        return JsonResponse(
            {"success": True, "message": "Settings successfully saved."}, status=200
        )
    return JsonResponse(
        {"success": False, "message": "Only POST requests are allowed."}, status=405
    )


# <--- AI Settings --->


def load_ai_settings(request):
    if request.method != "GET":
        return JsonResponse(
            {"success": False, "message": "Only GET requests are allowed."}, status=405
        )

    return JsonResponse(
        load_settings_from_file(
            CUSTOM_AI_SETTINGS_FILE_STEM, DEFAULT_AI_SETTINGS_FILE_STEM
        )
    )


def save_ai_settings(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Only POST requests are allowed."}, status=405
        )

    ai_settings = json.loads(request.body.decode("utf-8"))
    op = YamlOperator()
    path = SETTINGS_PATH / f"{CUSTOM_AI_SETTINGS_FILE_STEM}.yaml"
    try:
        op.write(path, ai_settings)
    except:
        return JsonResponse({"success": False, "message": "Saving failed!"}, status=400)

    return JsonResponse(
        {"success": True, "message": "Settings successfully saved."}, status=200
    )


def send_chat_message(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Only POST requests are allowed."}, status=405
        )

    data = json.loads(request.body.decode("utf-8"))
    messages = data.get("messages", [])
    ai_settings = load_settings_from_file(
        CUSTOM_AI_SETTINGS_FILE_STEM, DEFAULT_AI_SETTINGS_FILE_STEM
    )
    provider = ai_settings.get("provider", "")
    model = ai_settings.get("model", "")
    api_key = ai_settings.get("api_key", "")

    if not messages or not provider or not model or not api_key:
        return JsonResponse(
            {"success": False, "message": "AI settings or chat message missing."},
            status=400,
        )

    if "/" not in model and provider not in {"openai", "chatgpt"}:
        model = f"{provider}/{model}"

    def stream():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            stream_iterator = _stream_chat_message_with_langchain(
                model, api_key, messages
            ).__aiter__()
            while True:
                try:
                    chunk = loop.run_until_complete(stream_iterator.__anext__())
                except StopAsyncIteration:
                    break
                yield json.dumps(chunk) + "\n"
        except Exception as error:
            yield json.dumps({"type": "error", "message": str(error)}) + "\n"
        finally:
            if "loop" in locals():
                loop.close()

    return StreamingHttpResponse(stream(), content_type="application/x-ndjson")


def get_ai_providers(request):
    if request.method != "GET":
        return JsonResponse(
            {"success": False, "message": "Only GET requests are allowed."}, status=405
        )

    return JsonResponse(
        [_litellm_value(provider) for provider in litellm.provider_list], safe=False
    )


def get_ai_models(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Only POST requests are allowed."}, status=405
        )

    data = json.loads(request.body.decode("utf-8"))
    provider = data.get("provider", "")
    if provider.startswith("LlmProviders."):
        provider = provider.removeprefix("LlmProviders.").lower()

    models = litellm.models_by_provider.get(provider, [])
    return JsonResponse([str(model) for model in models], safe=False)


def download_plot(request):
    if request.method == "POST":
        params = json.loads(request.body.decode("utf-8"))
        fig = go.Figure(json.loads(params["plot"]))
        file = get_plot_file(fig, params)
    return FileResponse(file)


def get_plot_file(fig: go.Figure, params: dict):
    file_format = params["fileFormat"]
    if file_format in ["eps", "tiff"]:
        fig_binary = pio.to_image(fig, format="png", scale=params["scale"])
        img = Image.open(BytesIO(fig_binary)).convert("RGB")
        binary = BytesIO()
        args = {"format": file_format}
        if file_format == "tiff":
            args["compression"] = "tiff_lzw"
        img.save(binary, **args)
    elif file_format == "pdf":
        img = pio.to_image(fig, format=file_format, scale=params["scale"])
        binary = BytesIO(img)
    binary.seek(0)
    return binary


# <--- PTM Settings --->


def load_ptm_settings(request, default_file_stem: str = DEFAULT_PTM_SETTINGS_FILE_STEM):
    return load_settings(request, default_file_stem)


def load_default_ptm_settings_as_yaml(request):
    try:
        example_settings = load_yaml_from_file(
            SETTINGS_PATH / f"{DEFAULT_PTM_SETTINGS_FILE_STEM}.yaml"
        )
    except:
        return JsonResponse(
            {"success": False, "message": "Couldn't load default settings from file."},
            status=400,
        )

    return JsonResponse({"example_settings": example_settings})


def _load_dict_from_yaml_file(request, filename: str) -> tuple[dict | None, str]:
    path = settings.FILE_UPLOAD_TEMP_DIR / filename
    if path.suffix != ".yaml":
        msg = "File must be a YAML file with the extension .yaml"
        messages.add_message(request, messages.ERROR, msg, "alert-danger")
        return None, msg
    try:
        data = YamlOperator().read(path)
    except UnicodeDecodeError:
        msg = "File could not be decoded."
        messages.add_message(request, messages.ERROR, msg, "alert-danger")
        return None, msg
    return data, ""


def load_modification_settings_from_upload(
    request, old_settings, ptm_settings_filename: str
) -> tuple[dict | None, str]:
    modification_settings, msg = _load_dict_from_yaml_file(
        request, ptm_settings_filename
    )
    if modification_settings is None:
        return None, msg

    # Modifications should be overwritten, so that user can also remove modifications. Other stuff should retain the
    # same keys and thus also old values for unchanged keys.
    merged = old_settings
    if "modifications" in modification_settings:
        merged["modifications"] = modification_settings["modifications"]
    if "color_settings" in modification_settings:
        merged["color_settings"] = dict(
            old_settings["color_settings"], **modification_settings["color_settings"]
        )
    if "other_settings" in modification_settings:
        merged["other_settings"] = dict(
            old_settings["other_settings"], **modification_settings["other_settings"]
        )
    return merged, ""


def save_ptm_settings(request, default_file_stem: str = DEFAULT_PTM_SETTINGS_FILE_STEM):
    if not request.method == "POST":
        return JsonResponse(
            {"success": False, "message": "Only POST requests are allowed."}, status=405
        )

    ptm_settings_yaml_path = SETTINGS_PATH / f"{CUSTOM_PTM_SETTINGS_FILE_STEM}.yaml"
    op = YamlOperator()
    if not ptm_settings_yaml_path.exists():
        default_settings_yaml_path = SETTINGS_PATH / f"{default_file_stem}.yaml"
        old_settings = op.read(default_settings_yaml_path)
    else:
        old_settings = op.read(ptm_settings_yaml_path)

    request_args = json.loads(request.body.decode("utf-8"))
    if (ptm_settings_filename := request_args.get("ptm_settings_file", "")) != "":
        modification_settings, msg = load_modification_settings_from_upload(
            request, old_settings, ptm_settings_filename
        )
        if modification_settings is None:
            return JsonResponse({"success": False, "message": msg}, status=400)

    for _, mod_settings in modification_settings["modifications"].items():
        if not (
            "above_below" in mod_settings
            and isinstance(mod_settings["above_below"], str)
            and "color" in mod_settings
            and isinstance(mod_settings["color"], str)
            and "name" in mod_settings
            and isinstance(mod_settings["name"], str)
            and "sites" in mod_settings
            and isinstance(mod_settings["sites"], list)
        ):

            return JsonResponse(
                {
                    "success": False,
                    "message": "Provided modifications need to specify 'above_below' ('A'/'B'), 'color' (as hex "
                    "string), 'name' (string) and 'sites' (list of amino acids). Refer to the default "
                    "settings for an example.",
                },
                status=400,
            )

    try:
        op.write(ptm_settings_yaml_path, modification_settings)
    except:
        return JsonResponse({"success": False, "message": "Saving failed!"}, status=400)

    return JsonResponse(
        {"success": True, "message": "Settings successfully saved."}, status=200
    )


# <--- Databases --->


def get_databases(request):
    databases = uniprot_databases()
    df_infos = []
    # second check avoids errors if the metadata is somehow empty and thus prevents the database listing from displaying
    if DATABASE_METADATA_PATH.exists() and os.path.getsize(DATABASE_METADATA_PATH) > 0:
        with open(DATABASE_METADATA_PATH, "r") as f:
            database_metadata = json.load(f)
    else:
        database_metadata = {}

    for db in databases:
        database = dict(
            name=db,
            cols=uniprot_columns(db),
            filesize=database_path(db).stat().st_size,
            date=database_metadata.get(db, {}).get("date", ""),
            num_proteins=database_metadata.get(db, {}).get("num_proteins", 0),
        )
        df_infos.append(database)
    return JsonResponse(df_infos, safe=False)


def database_upload(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")
        file_name = data.get("file")
        path = settings.FILE_UPLOAD_TEMP_DIR / file_name

        converted_name, message = sanitize_name(name)

        if converted_name is None or converted_name == "":
            msg = "Filename cannot be empty."
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return JsonResponse({"success": False, "message": msg}, status=400)

        if database_path(converted_name).exists():
            msg = "Filename already taken."
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return JsonResponse({"success": False, "message": msg}, status=400)

        if not (EXTERNAL_DATA_PATH / "uniprot").exists():
            (EXTERNAL_DATA_PATH / "uniprot").mkdir(parents=True)

        just_copy_string = data.get("just_copy", False)
        if just_copy_string == "True":
            shutil.copy(path, database_path(converted_name))
            num_proteins = 0
        else:
            if path.suffix != ".tsv":
                msg = "File must be a tab-separated file with the extension .tsv"
                messages.add_message(request, messages.ERROR, msg, "alert-danger")
                return JsonResponse({"success": False, "message": msg}, status=400)

            try:
                dataframe = pandas.read_csv(path, sep="\t")
            except UnicodeDecodeError:
                msg = "File could not be decoded."
                messages.add_message(request, messages.ERROR, msg, "alert-danger")
                return JsonResponse({"success": False, "message": msg}, status=400)

            if "Entry" not in dataframe.columns:
                msg = "Required 'Entry' column not found."
                messages.add_message(request, messages.ERROR, msg, "alert-danger")
                return JsonResponse({"success": False, "message": msg}, status=400)

            dataframe.to_csv(database_path(converted_name), sep="\t", index=False)
            num_proteins = len(dataframe)

        if not DATABASE_METADATA_PATH.parent.exists():
            DATABASE_METADATA_PATH.parent.mkdir(parents=True)

        if DATABASE_METADATA_PATH.exists():
            with open(DATABASE_METADATA_PATH, "r") as f:
                database_metadata = json.load(f)
        else:
            database_metadata = {}
        database_metadata[converted_name] = dict(
            num_proteins=num_proteins, date=date.today().isoformat()
        )
        with open(DATABASE_METADATA_PATH, "w") as f:
            json.dump(database_metadata, f)

        return JsonResponse(
            {
                "success": True,
                "message": (
                    f"Database uploaded successfully. \n {message}"
                    if len(message) > 0
                    else "Database uploaded successfully"
                ),
            },
            status=200,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def database_delete(request):
    if request.method == "POST":
        data = json.loads(request.body)
        database_name = data.get("name")
        path = database_path(database_name)
        path.unlink()

        if DATABASE_METADATA_PATH.exists():
            with open(DATABASE_METADATA_PATH, "r") as f:
                database_metadata = json.load(f)

            if database_name in database_metadata:
                del database_metadata[database_name]
                with open(DATABASE_METADATA_PATH, "w") as f:
                    json.dump(database_metadata, f)

        return JsonResponse(
            {"success": True, "message": "Database deleted successfully"}, status=200
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def database_path(name):
    return EXTERNAL_DATA_PATH / "uniprot" / f"{name}.tsv"
