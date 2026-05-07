import json
import pytest
from unittest import mock
from django.http import JsonResponse

from backend.main.views_settings import (
    get_cl_defaults,
    update_cl_default,
    delete_cl_default,
)

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.main.settings")
if not django.apps.apps.ready:
    django.setup()

PATCH_PATH = "backend.main.views_settings.DefaultsOperator"


def test_get_cl_defaults(monkeypatch):
    request = mock.Mock()
    request.method = "GET"

    mock_defaults_operator = mock.Mock()
    mock_defaults_operator.read_default.return_value = {
        "DSSO": {
            "cl_length": 10.3,
            "cl_upper_deviation": 1.0,
            "cl_lower_deviation": 1.0,
        }
    }
    monkeypatch.setattr(PATCH_PATH, lambda: mock_defaults_operator)

    response = get_cl_defaults(request)

    assert response.status_code == 200
    response_data = json.loads(response.content.decode("utf-8"))
    assert response_data == {
        "DSSO": {
            "cl_length": 10.3,
            "cl_upper_deviation": 1.0,
            "cl_lower_deviation": 1.0,
        }
    }


def test_update_cl_default_success(monkeypatch):
    payload = {
        "cl_name": "DSSO",
        "cl_length": 10.3,
        "cl_upper_deviation": 1.0,
        "cl_lower_deviation": 1.2,
    }

    request = mock.Mock()
    request.method = "POST"
    request.body = json.dumps(payload).encode("utf-8")

    mock_defaults_operator = mock.Mock()
    mock_defaults_operator.read_default.return_value = {}
    monkeypatch.setattr(PATCH_PATH, lambda: mock_defaults_operator)

    response = update_cl_default(request)

    mock_defaults_operator.write_default.assert_called_once_with(
        name="crosslinker_lengths",
        value={
            "DSSO": {
                "cl_length": 10.3,
                "cl_upper_deviation": 1.0,
                "cl_lower_deviation": 1.2,
            }
        },
    )
    assert response.status_code == 200
    response_data = json.loads(response.content.decode("utf-8"))
    assert response_data["success"] is True


def test_update_cl_default_exception(monkeypatch):
    payload = {"cl_name": "DSSO", "cl_length": 10.3}

    request = mock.Mock()
    request.method = "POST"
    request.body = json.dumps(payload).encode("utf-8")

    mock_defaults_operator = mock.Mock()
    mock_defaults_operator.write_default.side_effect = Exception("Disk write failed")
    monkeypatch.setattr(PATCH_PATH, lambda: mock_defaults_operator)

    response = update_cl_default(request)

    assert response.status_code == 405
    response_data = json.loads(response.content.decode("utf-8"))
    assert response_data["success"] is False


def test_delete_cl_default_success(monkeypatch):
    payload = {"cl_name": "DSSO"}

    request = mock.Mock()
    request.method = "POST"
    request.body = json.dumps(payload).encode("utf-8")

    mock_defaults_operator = mock.Mock()
    mock_defaults_operator.read_default.return_value = {"DSSO": {"cl_length": 10.3}}
    monkeypatch.setattr(PATCH_PATH, lambda: mock_defaults_operator)

    response = delete_cl_default(request)

    mock_defaults_operator.write_default.assert_called_once_with(
        name="crosslinker_lengths", value={}
    )

    assert response.status_code == 200
    response_data = json.loads(response.content.decode("utf-8"))
    assert response_data["success"] is True


def test_delete_cl_default_exception(monkeypatch):
    payload = {"cl_name": "DSSO"}

    request = mock.Mock()
    request.method = "POST"
    request.body = json.dumps(payload).encode("utf-8")

    mock_defaults_operator = mock.Mock()
    mock_defaults_operator.delete_default.side_effect = Exception("Disk delete failed")
    monkeypatch.setattr(PATCH_PATH, lambda: mock_defaults_operator)

    response = delete_cl_default(request)

    assert response.status_code == 405
    response_data = json.loads(response.content.decode("utf-8"))
    assert response_data["success"] is False
