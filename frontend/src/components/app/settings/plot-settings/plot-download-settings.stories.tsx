import { color } from "@protzilla/theme";
import { Data, Layout } from "plotly.js";

import { PlotDownloadSettings, PlotDownloadSettingsProps } from "./plot-download-settings";

export default {
  component: PlotDownloadSettings,
  title: "Settings Components / Plot Download",
};

export const primary = (args: PlotDownloadSettingsProps): React.ReactNode => (
  <PlotDownloadSettings {...args} />
);

const exampleData = [
  {
    marker: { color: color("protzillaDarkBlue") },
    x: ["Example 1"],
    y: [0.7],
    name: "Example 1",
    type: "bar",
  },
  {
    marker: { color: color("protzillaRed") },
    x: ["Example 2"],
    y: [0.3],
    name: "Example 2",
    type: "bar",
  },
] as Data;
const exampleLayout = {
  width: 400,
  height: 250,
  title: {
    font: { family: "Sans Serif", size: 15 },
    text: "Very important title",
  },
  xaxis: { anchor: "y", title: { text: "x-axis" } },
  yaxis: { anchor: "x", title: { text: "y-axis" } },
  template: {
    layout: {
      colorway: ["#4A536A", "#CE5A5A"],
      dragmode: "pan",
      font: { family: "Sans Serif", size: 10 },
      margin: { b: 55, t: 50, r: 50, l: 50 },
      modebar: {
        remove: ["autoScale2d", "lasso", "lasso2d", "toImage", "select2d"],
      },
      plot_bgcolor: "white",
      title: {
        x: 0.5,
        xanchor: "center",
        y: 0.95,
        yanchor: "top",
      },
      yaxis: { gridcolor: "lightgrey", zerolinecolor: "lightgrey" },
    },
  },
} as Partial<Layout>;

primary.args = {
  isOpen: true,
  data: exampleData,
  layout: exampleLayout,
};
