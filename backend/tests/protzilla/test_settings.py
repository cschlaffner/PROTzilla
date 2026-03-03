import copy
import json
import shutil
from pathlib import Path
from unittest import mock

import yaml
import pytest
from django.test.client import RequestFactory

from backend.main import settings, views_settings
from backend.main.views_settings import (
    save_ptm_settings,
    load_ptm_settings,
    load_default_ptm_settings_as_yaml,
)
from backend.protzilla.constants.paths import (
    SETTINGS_PATH,
    DEFAULT_PTM_SETTINGS_FILE_STEM,
    CUSTOM_PTM_SETTINGS_FILE_STEM,
)


@pytest.fixture
def request_save_ptm_settings():
    rf = RequestFactory()
    request = rf.post(
        "api/save_ptm_settings",
        {"ptm_settings_file": "TEST_ptm_settings.yaml"},
        content_type="application/json",
    )
    return request


@pytest.fixture
def request_load_ptm_settings():
    rf = RequestFactory()
    request = rf.post(
        "api/load_ptm_settings",
        {"templateName": "TEST_ptm_settings"},
        content_type="application/json",
    )
    return request


@pytest.fixture()
def tmp_settings_dir(tmp_path_factory):
    test_tmp_data_dir = Path("ptm_settings/")
    tmp_path = tmp_path_factory.mktemp(str(test_tmp_data_dir))
    return tmp_path


@pytest.fixture()
def tmp_upload_dir(tmp_path_factory):
    tmp_upload_dir = Path("uploads/")
    tmp_path = tmp_path_factory.mktemp(str(tmp_upload_dir))
    settings_file = SETTINGS_PATH / f"{DEFAULT_PTM_SETTINGS_FILE_STEM}.yaml"
    shutil.copyfile(settings_file, tmp_path / f"TEST_ptm_settings.yaml")
    return tmp_path


@pytest.fixture()
def new_ptm_settings():
    default_settings_file = SETTINGS_PATH / f"{DEFAULT_PTM_SETTINGS_FILE_STEM}.yaml"
    with default_settings_file.open() as file:
        return yaml.safe_load(file)


def test_save_ptm_settings(
    request_save_ptm_settings,
    request_load_ptm_settings,
    new_ptm_settings,
    tmp_settings_dir,
    tmp_upload_dir,
):
    # write new settings to temp upload dir
    new_settings_file_stem = "TEST_ptm_settings"
    new_settings_file = tmp_upload_dir / f"{new_settings_file_stem}.yaml"
    with new_settings_file.open("w") as file:
        yaml.dump(new_ptm_settings, file)

    default_ptm_settings_file = SETTINGS_PATH / f"{DEFAULT_PTM_SETTINGS_FILE_STEM}.yaml"
    shutil.copy(default_ptm_settings_file, tmp_settings_dir)

    with (
        mock.patch.object(
            views_settings, "SETTINGS_PATH", tmp_settings_dir.resolve()
        ),
        mock.patch.object(
            settings, "FILE_UPLOAD_TEMP_DIR", tmp_upload_dir.resolve()
        ),
    ):
        save_response = save_ptm_settings(
            request_save_ptm_settings, default_file_stem=DEFAULT_PTM_SETTINGS_FILE_STEM
        )
        assert save_response.status_code == 200
        message = json.loads(save_response.content.decode("utf-8"))["message"]
        assert message == "Settings successfully saved."

        # read new settings from file (manually)
        ptm_settings_path = tmp_settings_dir / f"{CUSTOM_PTM_SETTINGS_FILE_STEM}.yaml"
        with ptm_settings_path.open() as file:
            saved_settings = yaml.safe_load(file)
        assert saved_settings == new_ptm_settings

        # read new settings from file using API endpoint
        load_response = load_ptm_settings(
            request_load_ptm_settings, default_file_stem=DEFAULT_PTM_SETTINGS_FILE_STEM
        )
        assert load_response.status_code == 200
        response_data = json.loads(load_response.content.decode("utf-8"))
        assert response_data == new_ptm_settings


def test_save_ptm_settings_malformed_settings(
    request_save_ptm_settings,
    new_ptm_settings,
    tmp_settings_dir,
    tmp_upload_dir,
):
    """Test that save_ptm_settings fails when modifications are malformed."""
    missing_key_test_cases = [
        ("sites", lambda settings: settings["modifications"]["Acetyl"].pop("sites")),
        ("name", lambda settings: settings["modifications"]["Acetyl"].pop("name")),
        ("color", lambda settings: settings["modifications"]["Acetyl"].pop("color")),
        (
            "above_below",
            lambda settings: settings["modifications"]["Acetyl"].pop("above_below"),
        ),
    ]

    default_ptm_settings_file = SETTINGS_PATH / f"{DEFAULT_PTM_SETTINGS_FILE_STEM}.yaml"
    shutil.copy(default_ptm_settings_file, tmp_settings_dir)

    for missing_key_description, modify_settings_func in missing_key_test_cases:
        # Create malformed settings by removing a specific key
        malformed_ptm_settings = copy.deepcopy(new_ptm_settings)
        modify_settings_func(malformed_ptm_settings)

        # write malformed settings to temp upload dir
        new_settings_file_stem = "TEST_ptm_settings"
        new_settings_file = tmp_upload_dir / f"{new_settings_file_stem}.yaml"
        with new_settings_file.open("w") as file:
            yaml.dump(malformed_ptm_settings, file)

        with (
            mock.patch.object(
                views_settings, "SETTINGS_PATH", tmp_settings_dir.resolve()
            ),
            mock.patch.object(
                settings, "FILE_UPLOAD_TEMP_DIR", tmp_upload_dir.resolve()
            ),
        ):
            save_response = save_ptm_settings(
                request_save_ptm_settings,
                default_file_stem=DEFAULT_PTM_SETTINGS_FILE_STEM,
            )
            assert (
                save_response.status_code == 400
            ), f"Expected 400 status when missing key: {missing_key_description}"
            message = json.loads(save_response.content.decode("utf-8"))["message"]
            # The exact error message may vary depending on which key is missing
            assert "Provided modifications need to specify" in message


def test_ptm_settings_load_default():
    default_settings_file = SETTINGS_PATH / f"{DEFAULT_PTM_SETTINGS_FILE_STEM}.yaml"
    with default_settings_file.open() as file:
        default_settings_string = file.read()

    rf = RequestFactory()
    load_default_request = rf.get("api/load_default_ptm_settings")
    default_response = load_default_ptm_settings_as_yaml(load_default_request)
    assert default_response.status_code == 200
    response_data = json.loads(default_response.content.decode("utf-8"))
    assert response_data["example_settings"] == default_settings_string


def test_ptm_settings_get_request():
    rf = RequestFactory()
    save_request = rf.get("api/save_ptm_settings")
    save_response = save_ptm_settings(save_request)
    assert save_response.status_code == 405
    message = json.loads(save_response.content.decode("utf-8"))["message"]
    assert message == "Only POST requests are allowed."

    load_request = rf.get("api/load_ptm_settings")
    load_response = load_ptm_settings(load_request)
    assert load_response.status_code == 405
    message = json.loads(load_response.content.decode("utf-8"))["message"]
    assert message == "Only POST requests are allowed."
