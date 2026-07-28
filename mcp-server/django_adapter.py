import os

import requests


API_ROOTS = [
    os.getenv("PROTZILLA_API_URL", "http://127.0.0.1:8000/api"),
    "http://localhost:5173/api",
]


def post(endpoint: str, *, allow_error_data: bool = False, **data) -> dict:
    connection_error = None
    for api_root in dict.fromkeys(API_ROOTS):
        try:
            response = requests.post(
                f"{api_root.rstrip('/')}/{endpoint.strip('/')}/", json=data
            )
            result = response.json()
        except requests.ConnectionError as error:
            connection_error = error
            continue
        except ValueError as error:
            raise ValueError(
                f"Django returned an invalid response (HTTP {response.status_code})."
            ) from error

        if result.get("success"):
            return result.get("data", {})
        if allow_error_data and result.get("data"):
            return result["data"]

        message = result.get("message", response.text)
        if isinstance(message, dict):
            message = message.get("msg", str(message))
        raise ValueError(message)

    raise ValueError(
        "Could not reach the PROTzilla Django API. :("
    ) from connection_error
