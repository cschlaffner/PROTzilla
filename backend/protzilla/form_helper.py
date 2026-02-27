from backend.protzilla.constants.data_types import DataKeys, StepID
from backend.protzilla.form import Option
from backend.protzilla.run import Run
from backend.protzilla.steps import Step


def to_choices(choices: list[str], required: bool = True) -> list[Option]:
    return (
        [Option(str(el), str(el)) for el in choices] + [Option(None, "---------")]
        if not required
        else [Option(str(el), str(el)) for el in choices]
    )


def get_choices_for_protein_df_steps(run: Run) -> list[Option]:
    options = to_choices(run.steps.get_instance_identifiers(Step, "protein_df"))
    return list(reversed(options))


def get_choices_for_protein_ids(
    run: Run, instance_identifier: StepID, output_key: DataKeys
) -> list[Option]:
    protein_df = run.steps.get_step_output(
        output_key="protein_df",
        instance_identifier=instance_identifier,
    )
    if protein_df is not None:
        protein_ids = protein_df["Protein ID"].unique().tolist()
        return to_choices(protein_ids)
    return []


def get_choices(
    run: Run,
    output_key: str,
    step_type: type[Step] = Step,
    required: bool = True,
) -> list[Option]:
    """
    Returns the instance identifiers containing the passed output key.
    :param run: the run object
    :param output_key: the output key (e.g. "protein_df" or "enrichment_df")
    :return: a list of tuples containing the instance identifier and the instance identifier
    """
    choices = to_choices(
        run.steps.get_instance_identifiers(step_type, output_key), required=required
    )
    return list(reversed(choices))


def get_choices_for_metadata(
    run: Run,
    instance_identifier: StepID,
    output_key: DataKeys,
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
    output_key: DataKeys,
    groups_column: str,
    required: bool = True,
) -> list[Option]:
    metadata_df = run.steps.get_step_output(
        output_key=output_key, instance_identifier=instance_identifier
    )
    if metadata_df is None:
        return []
    return to_choices(metadata_df[groups_column].unique(), required)
