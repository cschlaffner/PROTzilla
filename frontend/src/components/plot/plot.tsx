import React from "react";
import Plot from "react-plotly.js";
import { styled, useTheme } from "styled-components";

import { PlotProps } from "./plot.props";
import { border, borderColors } from "../../theme";

const PlotDiv = styled.div`
  width: fit-content;
  height: fit-content;
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
`;

export const PlotComponent: React.FC<PlotProps> = ({ data, layout, divId }) => {
  const theme = useTheme();
  return (
    <PlotDiv>
      <div style={{ margin: theme.borders.defaultStrength }}>
        <Plot data={data} layout={layout} divId={divId} />
      </div>
    </PlotDiv>
  );
};

export default PlotComponent;
