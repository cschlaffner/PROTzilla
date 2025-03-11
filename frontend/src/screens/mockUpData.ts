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
  label: "Max ",
  isAutoSubmit: true,
  input_fields: [
    {
      type: "text",
      name: "username",
      props: { label: "Username" },
    },
    {
      type: "number",
      name: "age",
      props: { label: "Age" },
    },
    {
      type: "multi-select",
      name: "country",
      props: {
        label: "Country",
        options: [
          { label: "Deutschland", value: "DE" },
          { label: "Österreich", value: "AT" },
          { label: "Schweiz", value: "CH" },
          { label: "Frankreich", value: "FR" },
          { label: "Italien", value: "IT" },
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
