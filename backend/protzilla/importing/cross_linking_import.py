"""
This module contains the code to parse a file containing cross linking data.
"""

import logging
from pathlib import Path
import pandas as pd
import traceback

from backend.protzilla.utilities import format_trace

def cross_linking_import(
    file_path: Path,
) -> dict:
    try:
        df = pd.read_csv(
            file_path,
            sep="\t",
            low_memory=False,
            na_values=["", 0],
            keep_default_na=True,
        )
    except Exception as e:
        msg = f"An error occurred while reading the file: {e.__class__.__name__} {e}. Please provide a valid cross linking file."
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=msg,
                    trace=format_trace(traceback.format_exception(e)),
                )
            ]
        )