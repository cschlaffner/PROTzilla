from backend.protzilla.constants import paths


def get_available_workflow_names() -> list[str]:
    if not paths.WORKFLOWS_PATH.exists():
        return []
    return [
        file.stem
        for file in paths.WORKFLOWS_PATH.iterdir()
        if not file.name.startswith(".")
        and file.suffix == ".yaml"
        and not file.name.endswith(".file_input_map.yaml")
    ]


def delete_workflow_file(name: str) -> tuple[bool, str]:
    workflow_path = paths.WORKFLOWS_PATH / f"{name}.yaml"
    file_input_map_path = paths.WORKFLOWS_PATH / f"{name}.file_input_map.yaml"
    if workflow_path.exists():
        workflow_path.unlink()
        if file_input_map_path.exists():
            file_input_map_path.unlink()
        return (True, "")
    else:
        return (False, workflow_path)
