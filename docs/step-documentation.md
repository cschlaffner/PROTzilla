# Step Documentation

PROTzilla workflows are built from individual steps. Each step performs one specific task, such as importing a file, filtering proteins, running a statistical test, or creating a plot.

## Step Categories

Each step is assigned to one of the following categories:

1. [Importing](importing): Loads external data into PROTzilla and converts it into internal data structures.
2. [Data Preprocessing](data-preprocessing): Cleans, filters, transforms, normalizes, or imputes data to prepare it for analysis.
3. [Data Analysis](data-analysis): Applies statistical, machine learning, or visualization methods to extract insights from the prepared data.
4. [Data Integration](data-integration): Combines, maps, annotates, or links data from multiple sources to enrich or contextualize the analysis.
5. [Custom Steps](step-documentation/custom-steps.md): Runs user-defined Python code as part of a workflow.

## What Is a Step?

A step represents a single operation in a PROTzilla workflow. It receives data through its input connections, processes that data according to its parameters, and may provide one or more outputs for subsequent steps.

The available parameters depend on the selected step. Some steps require files or metadata, while others operate on results produced by earlier steps.

## Inputs and Outputs

Steps exchange data through typed input and output connections. For example, an importing step may produce a `protein_df`, which can then be connected to the `protein_df` input of a preprocessing step.

Only compatible inputs and outputs should be connected. (PROTzilla does not enforce this, so incompatible connections are possible but may cause errors during calculation). 

A step may also produce tables, plots, lists, or other results that are displayed in the PROTzilla interface without being used by another step.
