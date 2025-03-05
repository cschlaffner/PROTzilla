import React from "react";

import { PlotComponent } from "./plot";
import { PlotProps } from "./plot.props";

export default {
  component: PlotComponent,
  title: "Plot",
};

export const primary = (args: PlotProps): React.ReactNode => (
  <PlotComponent {...args} />
);
primary.args = {
  data: [
    {
      x: ["A", "B", "C", "D"],
      y: [10, 20, 30, 40],
      type: "bar",
      marker: { color: "purple" },
    },
  ],
  layout: {
    title: { text: "Title"},
    xaxis: {
      anchor: "y",
      domain: [0.0, 1.0],
      title: { text: "Categories" }
    },
    yaxis: {
      anchor: "x",
      domain: [0.0, 1.0],
      title: { text: "Values" }
    }
  }
};