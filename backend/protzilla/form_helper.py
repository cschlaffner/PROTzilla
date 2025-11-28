import logging

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
    run: Run, output_key: str, step_type: type[Step] = Step
) -> list[Option]:
    """
    Returns the instance identifiers containing the passed output key.
    :param run: the run object
    :param output_key: the output key (e.g. "protein_df" or "enrichment_df"
    :return: a list of tuples containing the instance identifier and the instance identifier
    """
    choices = to_choices(run.steps.get_instance_identifiers(step_type, output_key))
    return list(reversed(choices))


def get_choices_for_metadata_non_sample_columns(run: Run) -> list[Option]:
    if run.steps.metadata_df is None:
        # TODO: should this rather be an error and raise an exception?
        logging.warning("No metadata_df found in run")
        return []
    return to_choices(
        run.steps.metadata_df.columns[
            run.steps.metadata_df.columns != "Sample"
        ].unique()
    )
