import React from "react";
import Plot from "react-plotly.js";

import { PlotProps } from "./plot.props";

export const PlotComponent: React.FC<PlotProps> = ({
  data,
  layout,
  styleProps,
}) => {
  return (
    <div style={styleProps}>
      <Plot data={data} layout={layout} />
    </div>
  );
};

export default PlotComponent;
