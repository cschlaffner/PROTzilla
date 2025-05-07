import Plot from "react-plotly.js";
import { styled, useTheme } from "styled-components";

import { PlotProps } from "./plot.props";
import { border, borderColors } from "../../theme";
import { SectionTitle } from "../section-title";

const PlotDiv = styled.div`
  width: fit-content;
  height: fit-content;
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
`;
//div style={{ width: "100%", height: "100%", flexGrow: 1, minHeight: 0 }}

export const PlotComponent: React.FC<PlotProps> = ({ data, layout, divId }) => {
  const theme = useTheme();
  return (
    <PlotDiv>
      {data.length > 0 ? (
        <div style={{ margin: theme.borders.defaultStrength }}>
          <Plot
            data={data}
            layout={{ ...layout, autosize: true }}
            style={{ width: "100%", height: "100%" }}
            useResizeHandler={true}
            divId={divId}
          />
        </div>
      ) : (
        <SectionTitle baseComponent={"h4"} description={"No plot available for this step."} />
      )}
    </PlotDiv>
  );
};
