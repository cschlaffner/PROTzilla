from backend.protzilla.form import Option
from backend.protzilla.run import Run
from backend.protzilla.steps import Step


def to_choices(choices: list[str], required: bool = True) -> list[Option]:
    return (
        [Option(el, el) for el in choices] + [Option(None, "---------")]
        if not required
        else [Option(el, el) for el in choices]
    )


def get_choices_for_protein_df_steps(run: Run) -> list[Option]:
    options = to_choices(run.steps.get_instance_identifiers(Step, "protein_df"))
    return list(reversed(options))


def get_choices(
    run: Run, output_key: str, step_type: type[Step] = Step
) -> list[Option]:
    """
    Returns the instance identifiers containing the passed output key.
    :param run: the run object
    :param output_key: the output key (e.g. "protein_df" or "enrichment_df")
    :return: a list of tuples containing the instance identifier and the instance identifier
    """
    choices = to_choices(run.steps.get_instance_identifiers(step_type, output_key))
    return list(reversed(choices))


def get_choices_for_metadata_non_sample_columns(run: Run, instance_identifier: str | None = None) -> list[Option]:
    if instance_identifier is None:
        metadata_df = run.steps.metadata_df
    else:
        metadata_df = run.steps.get_step_output(
            Step,
            output_key='metadata_df',
            instance_identifier=instance_identifier
        )
        if metadata_df is None:
            return []
    return to_choices(
        metadata_df.columns[
            metadata_df.columns != "Sample"
        ].unique()
    )
