import { FormData } from "../components/forms/form";

export const mockPlotData: Partial<Plotly.Data>[] = [
  {
    x: ["A", "B", "C", "D"],
    y: [10, 20, 30, 40],
    type: "bar",
    marker: { color: "purple" },
  },
];

export const mockPlotLayout: Partial<Plotly.Layout> = {
  title: { text: "Title" },
  xaxis: {
    anchor: "y",
    domain: [0.0, 1.0],
    title: { text: "Categories" },
  },
  yaxis: {
    anchor: "x",
    domain: [0.0, 1.0],
    title: { text: "Values" },
  },
};

export const mockFormDataParameters: FormData = {
  label: "Parameters",
  isAutoSubmit: false,
  input_fields: [
    {
      type: "dropdown",
      name: "method",
      props: {
        label: "Protein Data Import MaxQuant",
        options: [
          { label: "MaxQuant Protein Groups Import", value: "maxQuant" },
          { label: "MaxQuant Peptide Groups Import", value: "maxQuantPeptides" },
          { label: "MaxQuant MS/MS Data Import", value: "maxQuantMSMS" },
          { label: "MaxQuant Post-Processing", value: "maxQuantPostProcessing" },
        ],
      },
    },
    {
      type: "file",
      name: "file",
      props: { label: "MaxQuant intensities file (proteinGroups.txt):" },
    },
    {
      type: "dropdown",
      name: "intensity",
      props: {
        label: "Intensity",
        options: [
          { label: "iBAQ", value: "ibaq" },
          { label: "LFQ Intensity", value: "lfq" },
          { label: "Total Intensity", value: "totalIntensity" },
          { label: "Normalized Intensity", value: "normalizedIntensity" },
        ],
      },
    },
  ],
};


export const mockFormDataPlotSettings: FormData = {
  label: "Plot Settings",
  isAutoSubmit: true,
  input_fields: [
    {
      type: "dropdown",
      name: "type",
      props: {
        label: "Select a Plot type",
        options: [
          { label: "Bar", value: "bar" },
          { label: "Line", value: "scatter" },
        ],
      },
    },
    {
      type: "multi-select",
      name: "colors",
      props: {
        label: "Select colors for the plot",
        options: [
          { label: "Purple", value: "purple" },
          { label: "Blue", value: "blue" },
          { label: "Red", value: "red" },
          { label: "Yellow", value: "yellow" },
          { label: "Green", value: "green" },
          { label: "Cyan", value: "cyan" },
          { label: "Black", value: "black" },
        ],
      },
    },
  ],
};
