# Custom Steps

Custom steps run user-defined Python code as part of a PROTzilla workflow. They can receive data from other steps, process it using Python, and provide named outputs to subsequent steps.

> **Warning:** Custom step code is executed directly by the PROTzilla backend and is not sandboxed. Only run code from sources you trust.

## Inputs and Outputs

Each input and output has a **name** and a **type**.

- The name identifies the graph handle and becomes the variable name used in the Python code.
- The type describes the expected PROTzilla data structure, such as `protein_df`, `metadata_df`, or `custom_df`.

Names must be unique and valid Python identifiers. For example, `control_df` and `treatment_df` are valid names, while `control data` and `2nd_df` are not.

The selected type does not validate the contents at runtime. It primarily describes the handle in the graph. Connecting incompatible data may cause errors when the step is calculated.

Multiple handles may use the same type as long as they have different names:

| Type | Name |
| --- | --- |
| `protein_df` | `control_df` |
| `protein_df` | `treatment_df` |

An input that is not connected has the value `None` during calculation.

## Python Code

The code editor expects the body of a Python function. Do not include an additional `def` declaration.

The following values are available automatically:

- all connected inputs under their configured names,
- `pd` for pandas,
- `np` for NumPy,
- `default_intensity_column(...)` for retrieving the active protein-intensity column.

The code must return a dictionary. Every selected graph output must occur as a key in that dictionary:

```python
return dict(
    result_df=result_df,
)
```

Additional values may also be returned. They are stored as step results but do not become graph outputs unless a corresponding output handle is configured.

## Example: Filter by Protein IDs

Configure the handles as follows:

| Direction | Type | Name |
| --- | --- | --- |
| Input | `protein_df` | `protein_df` |
| Output | `protein_df` | `filtered_protein_df` |

```python
protein_ids = ["P00533", "Q9Y6K9", "A0A0B4J1V0"]
filtered_protein_df = protein_df[
    protein_df["Protein ID"].isin(protein_ids)
].copy()

return dict(
    filtered_protein_df=filtered_protein_df,
)
```

## Example: Filter Proteins by Sample Coverage

This example uses PROTzilla's `long_to_wide` utility. It must be imported explicitly because it is not included in the default custom-step namespace.

| Direction | Type | Name |
| --- | --- | --- |
| Input | `protein_df` | `control_df` |
| Output | `protein_df` | `filtered_control_df` |

```python
from backend.protzilla.utilities.transform_dfs import long_to_wide

percentage = 0.5

filter_threshold: int = percentage * len(control_df.Sample.unique())
transformed_df = long_to_wide(control_df)

remaining_proteins_list = transformed_df.dropna(
    axis=1,
    thresh=filter_threshold,
).columns.tolist()
filtered_proteins_list = (
    transformed_df.drop(remaining_proteins_list, axis=1)
    .columns.unique()
    .tolist()
)
filtered_df = control_df[
    control_df["Protein ID"].isin(remaining_proteins_list)
]

return dict(
    filtered_control_df=filtered_df,
    filtered_proteins=filtered_proteins_list,
    remaining_proteins=remaining_proteins_list,
)
```

The two protein lists are returned as additional step results. They do not become graph outputs unless corresponding output handles are configured.

## Example: Compare Two Protein Tables

This example receives two inputs of the same type and creates a new comparison table:

| Direction | Type | Name |
| --- | --- | --- |
| Input | `protein_df` | `control_df` |
| Input | `protein_df` | `treatment_df` |
| Output | `custom_df` | `comparison_df` |

```python
control_intensity = default_intensity_column(control_df)
treatment_intensity = default_intensity_column(treatment_df)

control_mean = (
    control_df.groupby("Protein ID")[control_intensity]
    .mean()
    .rename("control_mean")
)
treatment_mean = (
    treatment_df.groupby("Protein ID")[treatment_intensity]
    .mean()
    .rename("treatment_mean")
)

comparison_df = pd.concat(
    [control_mean, treatment_mean],
    axis=1,
).dropna()
comparison_df = comparison_df[
    (comparison_df["control_mean"] > 0)
    & (comparison_df["treatment_mean"] > 0)
].copy()
comparison_df["log2_fold_change"] = np.log2(
    comparison_df["treatment_mean"] / comparison_df["control_mean"]
)
comparison_df = comparison_df.reset_index()

return dict(
    comparison_df=comparison_df,
)
```

## Saved Custom Steps

The current configuration can be stored using **Save Custom Step**. A saved custom step contains its name, input handles, output handles, and Python code.

Saved steps are available under **Add Custom** and can be added to other runs as templates. You can find your saved custom steps under backend/user_data/custom_steps.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/methods/importing.py:custom_python_step"
```
