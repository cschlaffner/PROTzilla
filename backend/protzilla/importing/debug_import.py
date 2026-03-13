from pathlib import Path
import pandas as pd

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.steps import OutputItem, OutputType


def arbitrary_csv_import(
    file_path: Path,
) -> dict[DataKey, OutputItem]:
    return {
        DataKey.DEBUG: OutputItem(
            output_type=OutputType.DATAFRAME, value=pd.read_csv(file_path)
        )
    }
