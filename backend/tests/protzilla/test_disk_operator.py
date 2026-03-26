import pathlib

import pytest

from protzilla.disk_operator import YamlOperator


@pytest.fixture()
def tmp_output_dir(tmp_path_factory):
    test_tmp_data_dir = pathlib.Path("yaml_outputs/")
    tmp_path = tmp_path_factory.mktemp(str(test_tmp_data_dir))
    return tmp_path


def test_yaml_operator_path_handling(tmp_output_dir):
    # This test will (de)serialize a PosixPath on Linux/Mac and a WindowsPath on Windows. Unfortunately, it does not
    # seem to be possible to test both (de)serializations on a single platform, as pathlib will return an error if you
    # explicitly try to create a WindowsPath on Linux/Mac or a PosixPath on Windows.
    yaml_operator = YamlOperator()
    dummy_path = "/backend/user_data/runs/dummy/run.yaml"
    data_dict = {"file_path": pathlib.Path(dummy_path)}
    out_file_path = tmp_output_dir / "yaml_test.yaml"
    yaml_operator.write(out_file_path, data_dict)
    yaml_file_contents = yaml_operator.read(out_file_path)
    assert yaml_file_contents["file_path"] == pathlib.Path(dummy_path)
