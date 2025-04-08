import React from "react";
import Plot from "react-plotly.js";

import { PlotProps } from "./plot.props";

export const PlotComponent: React.FC<PlotProps> = ({ data, layout }) => {
  return (
    <div>
      <Plot data={data} layout={layout} />
    </div>
  );
};

export default PlotComponent;
