import React from "react";
import Plot from "react-plotly.js";

interface PlotProps {
  data: any[];
  layout: any;
}

const PlotComponent: React.FC<PlotProps> = ({ data, layout }) => {
  return (
    <div>
      <Plot data={data} layout={layout} />
    </div>
  );
};

export default PlotComponent;