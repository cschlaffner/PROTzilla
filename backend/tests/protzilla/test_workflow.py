import pytest

from unittest import mock
from pathlib import Path

from backend.protzilla.constants import paths
from backend.protzilla.workflow import get_available_workflow_names 

@pytest.fixture
def workflows_path(request):
    return Path(request.config.rootdir) / "/tests/test_workflows"

def test_get_available_workflow_names(workflows_path):
    with mock.patch.object(paths, "WORKFLOWS_PATH", paths.TEST_WORKFLOW_PATH):
        expected_files = [
            "example_workflow_short",
            "example_workflow"
        ]
        assert sorted(get_available_workflow_names()) == sorted(expected_files)
