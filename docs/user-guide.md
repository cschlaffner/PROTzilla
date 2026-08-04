# Installation

Before using PROTzilla, follow the installation guide for your operating system:

- [Linux](user-guide/Linux.md)
- [macOS](user-guide/MacOS.md)
- [Windows](user-guide/Windows.md)
- [Windows Server 2012](user-guide/WindowsServer2012.md)

# Quick Start
When launching PROTzilla, you can create a new **run** by choosing an existing **workflow** from the **Template Workflows** section. If you have previously worked on runs you can re-open them from the **Run Selection** section. When editing a run, you can add new **steps** using the respective add buttons for each step category. Within the **Flow Editor**, you can connect inputs and outputs of steps to each other by dragging from the little icons or arrows ("**handles**") associated with each step. You can select a step by clicking on it. For the selected step, a form with additional parameters as well as its outputs (i.e. plots and tables) will be displayed next to the Flow Editor. Runs are auto-saved with each operation you perform. To save your current workflow separately, click on the save icon in the centre of the top bar.

# Key Concepts in PROTzilla

## Workflow
A **workflow** is a sequence of steps with set parameters (that can differ from the default values) per step. It does not contain any data per se, only information on how data should be processed.

## Run
A **run** is an executed workflow with input data and all produced output files. It also contain its own metadata. The run may only be partially executed, meaning not all steps from the underlying workflow were calculated. 

Both runs and workflows can be imported and exported, making the sharing of research easy. Runs are exported as `.zip` files and must be imported as such, while exported and the to be imported workflows are `.yaml` files.

## Step
A **step** is a singular method or operation that transforms input data (either from a previous step or from a loaded file) into output data. If a step generates sufficient output data, this data can in turn be used as an input source for another step by connecting the respective handles of the steps to each other. Steps also commonly generate additional plots and graphs visualising the transformation of the data.

### Form
A step's **form** is the interface for passing additional calculation parameters to the step. The current selected step's form is always visible next to the Flow Editor.

### Handle
A **handle** is an input or output of a step that can be connected to other handles. Not necessarily all required inputs of a step are available as handles, as some must be specified as parameters in the form associated with each step. Most major calculation outputs (i.e. tables or lists) are available as output handles to then serve as inputs for other steps. Each handle is associated with a name that describes its purpose. By hovering over a handle, a tooltip in the top right of the Flow Editor will tell you whether or not the handle is an input or an output, as well as its name. Connect handles to each other by dragging them.

### Sections
Each step belongs to a section. PROTzilla currently supports 4 different sections, categorising all steps by similarity. 
The "Importing" section has all steps concerning the import of all kinds of protein and peptide data, as well as additional metadata such as sample or group mappings.
The "Data Preprocessing" section contains steps that are useful to prepare the data (e.g. using imputation, normalisation or filtering) before the actual analysis starts.
The "Data Analysis" section provides steps that perform different analyses.
The "Data Integration" section contains steps that allow additional external data to be used for further analysis.

# Additional Concepts

## PTM Visualization Settings

The settings of the PTM visualizations are controlled via a YAML file. 
An example can be downloaded from the settings page, modified as needed, and then uploaded again.
The settings are made up of three parts:

- modifications that should be displayed
- general color settings
- other settings

**Modifications**

This section consists of a list of modifications, each with associated key-value pairs.
The plots will only show modifications specified in this section, even if additional modifications were identified in the experiment.
(However, a warning will be displayed if more PTMs are found that were not configured.)

Each key of the list should be the name of the modification as found in the evidence.txt.
This then maps to: 
- `name`: a display name used in the plot
- `sites`: the amino acid shorthands where this modification can be found, e.g., `K` or `R`
- `color`: a hexadecimal color code to control how modifications are displayed in plots
- `above_below`: controls if a modification is plotted above or below the protein sequence

**General Color Settings**

- The color of cleavages can be controlled via `cleavage_label_color`. 
  Additionally, `cleavage_scale_color_high`, `cleavage_scale_color_low`, and `cleavage_scale_color_mid` can be used to control color scales used for the cleavages in the Details plot, setting the extrema and midpoint of the color scale.
- Similarly, the color scales for PTMs in the Details plot are controlled by `ptm_scale_color_high`, `ptm_scale_color_low`, and `ptm_scale_color_mid`.
- Different sequence regions (belonging to different isoforms) can be colored by assigning `A` and `B` in `sequence_region_colors` appropriate hex colors. In this case, `A` and `B` have to match the group defined in the metadata file for the regions.
- If you want to use your own colors for groups in the details plot, use `group_label_colors` and add a key-value pair for each group name.

**Other Settings**

- The protein sequence can be displayed vertically instead of horizontally by setting `vertical_orientation` to `false`.
- As implied, `label angles` controls the rotation of labels using an integer number that represents the degree of the angle.


# PROTzilla as a command line tool
A command line based runner for PROTzilla workflows is available via `runner_cli.py`. 
It allows you to run saved PROTzilla workflows from the command line, which can be useful for batch processing or automation tasks. 
The runner calculates a given dataset on a given workflow without the need for a graphical user interface.
It is recommended to adjust one of the template workflows `standard`, `only_import` and `only_import_and_filter_proteins` for your calculation needs via the regular PROTzilla user interface and then save it as a new workflow with the save icon right of the run's name.

Please be aware of the fact that the template workflows do not have all necessary fields specified and will fail if you try to run them without adjusting them first.

When a workflow is saved in the frontend, PROTzilla also creates a corresponding file input mapping file:
- `backend/user_data/workflows/<workflow_name>.file_input_map.yaml`

You can use this file as a starting point and replace the `null` values with the paths to your actual input files.

## Installing the local runner environment

The runner requires a local Python installation with the PROTzilla dependencies installed.
We recommend using Conda with Python 3.11.

**1. First, clone or download the PROTzilla repository and open a terminal in the PROTzilla directory:**
```bash
git clone https://github.com/cschlaffner/PROTzilla.git
cd PROTzilla
```
**2. Create and install the runner-environment:**

```bash
conda create -n protzilla-runner python=3.11
conda activate protzilla-runner
pip install -r requirements.txt
python install_scripts/database_download.py
conda deactivate
```

## Starting the command line interface

Before running the command line runner, make sure that the Conda environment is activated and that you are in the PROTzilla directory:

```bash
conda activate protzilla-runner
```
Then start the command line interface with:
```
python runner_cli.py -h
```
This will display the help message with all available options and arguments.

The general form is:
```bash
python runner_cli.py <workflow-name> <file-input-map-path> [options]
```

- workflow-name: Name of a workflow, saved in backend/user_data/workflows.
- file-input-map-path: Path to a YAML file using step_id -> {field_name: path}.
- [options]: 
  - --run-name <run-name> to set a custom name for the created run
  - --all-plots to save all generated plots as HTML files
  - --verbose to log the parsed CLI arguments

## Example 
```bash
python runner_cli.py my_modified_standard_workflow /path/to/my_modified_standard_workflow.file_input_map.yaml --run-name MyRunForTheRunner
```
This command runs the workflow `my_modified_standard_workflow` using the file inputs defined in `/path/to/my_modified_standard_workflow.file_input_map.yaml`.

A minimal file input mapping could look like this:

```yaml
s00001_MaxQuantImport:
  file_path: /path/to/proteinGroups.txt
s00014_MetadataImport:
  file_path: /path/to/meta_data.csv
```

## Troubleshooting
Please make sure to not have any spaces in the path to the input files or the workflow name or look up the correct escaping method
for your operating system. These will be handled as separate arguments and will lead to an error.

Errors on run execution will be printed to the console.
