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
    run: Run, instance_identifier: str | None = None
) -> list[Option]:
    if instance_identifier is None:
        metadata_df = run.steps.metadata_df
    else:
        metadata_df = run.steps.get_step_output(
            Step, output_key="metadata_df", instance_identifier=instance_identifier
        )
    if metadata_df is None:
        return to_choices([])
    return to_choices(metadata_df.columns.unique())


def get_choices_for_metadata_non_sample_columns(
    run: Run, instance_identifier: str | None = None
) -> list[Option]:
    metadata_choices = get_choices_for_metadata(run, instance_identifier)
    return [c for c in metadata_choices if c.label != "Sample"]


def get_crosslinker_names_from_crosslinker_df(run: Run) -> list[str]:
    df = run.steps.get_step_output(
        Step, output_key="crosslinking_df"
    )
    if df is None or "Crosslinker" not in df.columns:
        return []
    crosslinkers = df["Crosslinker"].dropna().unique()
    return crosslinkers
