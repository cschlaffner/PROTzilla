from backend.protzilla.constants.data_types import DataKey, StepID
from backend.protzilla.form import Option
from backend.protzilla.run import Run


def to_choices(choices: list[str], required: bool = True) -> list[Option]:
    return (
        [Option(str(el), str(el)) for el in choices] + [Option(None, "---------")]
        if not required
        else [Option(str(el), str(el)) for el in choices]
    )


def get_choices_for_df_columns(
    run: Run,
    step_id: StepID,
    output_key: DataKey,
    required: bool = True,
) -> list[Option]:
    target_df = run.steps.get_step_output(
        instance_identifier=step_id,
        output_key=output_key,
    )
    if target_df is None:
        return to_choices([])

    return to_choices(target_df.columns.unique().to_list(), required)


def get_choices_for_metadata(
    run: Run,
    instance_identifier: StepID,
    output_key: DataKey,
    include_sample: bool = True,
) -> list[Option]:
    metadata_df = run.steps.get_step_output(
        output_key=output_key, instance_identifier=instance_identifier
    )
    if metadata_df is None:
        return to_choices([])
    columns = (
        metadata_df.columns.unique().to_list()
        if include_sample
        else [column for column in metadata_df.columns.unique() if column != "Sample"]
    )
    return to_choices(columns)


def get_choices_for_groups(
    run: Run,
    instance_identifier: StepID,
    output_key: DataKey,
    groups_column: str,
    required: bool = True,
) -> list[Option]:
    metadata_df = run.steps.get_step_output(
        output_key=output_key, instance_identifier=instance_identifier
    )
    if metadata_df is None:
        return []
    return to_choices(metadata_df[groups_column].unique().tolist(), required)
