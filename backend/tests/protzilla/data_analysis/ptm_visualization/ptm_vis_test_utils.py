import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Optional
from unittest import mock

from _pytest.monkeypatch import MonkeyPatch

from backend.main.views_helper import load_settings_from_file
from backend.protzilla.constants.intensity_types import IntensityType
from backend.protzilla.constants.paths import SETTINGS_PATH
from backend.protzilla.data_analysis.ptm_visualization import ptm_vis_utils
from backend.protzilla.data_analysis.ptm_visualization.ptm_bar_plot import (
    create_bar_ptm_visualization,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_details_plot import (
    create_details_ptm_visualization,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    create_overview_ptm_visualization,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_vis_utils import (
    get_general_config_module,
)
from backend.protzilla.importing import peptide_import
from backend.protzilla.importing.metadata_import import metadata_import_method


def get_evidence_df(path: Path):
    outputs = peptide_import.evidence_import(
        file_path=path,
        # It's not really important for downstream tasks which intensity type we use, as long as it is in the
        # evidence df
        intensity_name=IntensityType.INTENSITY.value,
        map_to_uniprot=False,
    )
    evidence_df = outputs["psm_df"]
    return evidence_df


def get_metadata_df(path: Path):
    metadata_df = metadata_import_method(file_path=path, feature_orientation="columns")[
        "metadata_df"
    ]
    return metadata_df


def alter_general_config(monkeypatch: MonkeyPatch, new_param_dict: dict):
    def mock_update_settings(regions_file_path: Path, out_dir: Path):
        config_module = get_general_config_module(regions_file_path, out_dir)
        config_module.__dict__.update(new_param_dict)
        return config_module

    monkeypatch.setattr(
        ptm_vis_utils, "get_general_config_module", mock_update_settings
    )


@contextmanager
def mock_settings_file(new_settings_file_path: Path, tmp_dir: Path):
    shutil.copytree(SETTINGS_PATH, tmp_dir, dirs_exist_ok=True)
    shutil.copy(new_settings_file_path, tmp_dir)
    with (
        # Mocking is a bit more difficult because the values of default arguments are not overwritten once a function
        # is imported, so it would not be enough just to overwrite SETTINGS_PATH
        mock.patch.object(
            load_settings_from_file,
            "__defaults__",
            (
                load_settings_from_file.__defaults__[0],
                tmp_dir.resolve(),
            ),
        ),
        mock.patch.object(
            ptm_vis_utils,
            "CUSTOM_PTM_SETTINGS_FILE_STEM",
            new_settings_file_path.stem,
        ),
    ):
        yield


def get_region_range_for_exon_coords(
    exon_coords: list[tuple], horizontal_orientation: bool
) -> list[tuple[float, float]]:
    # A bit of complicated logic to define the region range for the exon. The side of the exon that is longer, includes
    # some buffer which is not actually part of the exon. Thus, we have to check which side is shorter and only include
    # this one in the valid region ranges.

    if not horizontal_orientation:
        exon_coords = [(e[1], e[0]) for e in exon_coords]

    new_regions = []
    for x, y in exon_coords:
        # figure out if the vertical line of the polygon is on the left or right side of the exon
        y_diff_indices = []
        for i in range(len(y) - 1):
            if y[i] != y[i + 1]:
                y_diff_indices.append(i)

        if x[y_diff_indices[0]] != x[y_diff_indices[0] + 1]:
            # vertical line at the beginning
            new_regions.append(tuple(sorted(set(x))[:2]))
        elif x[y_diff_indices[1]] != x[y_diff_indices[1] + 1]:
            # vertical line at the end
            new_regions.append(tuple(sorted(set(x))[1:]))
        else:
            assert False
    return new_regions


def validate_ptm_labels_in_bounds(plot):
    # Does an alignment check of the PTMs to assert that they are not overflowing the sequence or are plotted in
    # the exon gaps.
    # Should only be used for the overview plot, because in other plots we have way more shapes that make it
    # impossible to track what is shapes corresponds to regions and where the PTMs are located.
    all_shapes = plot.layout.shapes
    y_coords = {
        tuple(sorted((shape.y0, shape.y1)))
        for shape in all_shapes
        if shape.type == "rect"
    }
    x_coords = {
        tuple(sorted((shape.x0, shape.x1)))
        for shape in all_shapes
        if shape.type == "rect"
    }
    exon_coords = [
        (el.x, el.y)
        for el in plot.data
        if el.text is None and len(el.x) == 5 and len(el.y) == 5
    ]
    if len(y_coords) == 1:
        horizontal_orientation = True
        valid_region_ranges = x_coords
        valid_region_ranges.update(
            get_region_range_for_exon_coords(exon_coords, horizontal_orientation)
        )
    elif len(x_coords) == 1:
        horizontal_orientation = False
        valid_region_ranges = y_coords
        valid_region_ranges.update(
            get_region_range_for_exon_coords(exon_coords, horizontal_orientation)
        )
    else:
        raise AssertionError(
            "Rects of the sequence have to be aligned in one of the dimensions"
        )

    label_lines = [
        el for el in plot.data if el.text is None and len(el.x) == 2 and len(el.y) == 2
    ]
    for line in label_lines:
        if horizontal_orientation:
            assert len(set(line.x)) == 1
            assert any(r[0] <= line.x[0] <= r[1] for r in valid_region_ranges)
        else:
            assert len(set(line.y)) == 1
            assert any(r[0] <= line.y[0] <= r[1] for r in valid_region_ranges)


def validate_plot_outputs(
    plot,
    plot_func,
    all_groups: set,
    required_groups: set,
    validation_config: Optional["PlotValidationConfig"],
):
    if plot_func == create_overview_ptm_visualization:
        validate_ptm_labels_in_bounds(plot)

    all_layout_strings = {anno.text for anno in plot.layout.annotations if anno.text}
    all_data_strings = {
        subplot.text
        for subplot in plot.data
        if hasattr(subplot, "mode") and subplot.mode == "text"
    }
    all_plot_strings = all_layout_strings.union(all_data_strings)

    assert set(validation_config.required_ptm_types).issubset(all_plot_strings)
    assert set(validation_config.required_ptms).issubset(all_plot_strings)
    assert set(validation_config.required_region_names).issubset(all_plot_strings)

    if plot_func in (create_details_ptm_visualization, create_bar_ptm_visualization):
        required_groups = set(required_groups)
        assert required_groups.issubset(all_plot_strings)
        excluded_groups = all_groups - required_groups
        assert all(g not in all_plot_strings for g in excluded_groups)

    if plot_func == create_details_ptm_visualization:
        assert set(validation_config.required_cleavages).issubset(all_plot_strings)
        assert set(validation_config.required_region_short_names).issubset(
            all_plot_strings
        )

    assert all(s not in all_plot_strings for s in validation_config.excluded_strings)


def run_plot_and_validate(plot_func, kwargs, validation_config, required_groups):
    result = plot_func(**kwargs)
    assert len(result["plots"]) == 1
    plot = result["plots"][0]

    validate_plot_outputs(
        plot,
        plot_func,
        all_groups=(
            set(kwargs["metadata_df"]["Group"].unique())
            if "metadata_df" in kwargs
            else set()
        ),
        required_groups=required_groups,
        validation_config=validation_config,
    )
