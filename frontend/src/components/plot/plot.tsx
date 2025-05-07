import Plot from "react-plotly.js";
import { styled, useTheme } from "styled-components";

import { PlotProps } from "./plot.props";
import { border, borderColors } from "../../theme";
import { SectionTitle } from "../section-title";

const PlotDiv = styled.div<{ hasBorder: boolean }>`
  width: fit-content;
  height: fit-content;
  border: ${({ hasBorder }) => (hasBorder ? border("defaultStrength") : "none")} solid
    ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
`;

export const PlotComponent: React.FC<PlotProps> = ({ data, layout, hasBorder, divId }) => {
  const theme = useTheme();
  return (
    <div style={{ width: "100%", height: "100%", flexGrow: 1, minHeight: 0 }}>
      {data.length > 0 ? (
        <PlotDiv hasBorder={hasBorder ?? false}>
          <div style={{ margin: theme.borders.defaultStrength }}>
            <Plot
              data={data}
              layout={{ ...layout, autosize: false }}
              style={{ width: "100%", height: "100%" }}
              useResizeHandler={false}
              divId={divId}
            />
          </div>
        </PlotDiv>
      ) : (
        <SectionTitle baseComponent={"h4"} description={"No plot available for this step."} />
      )}
    </div>
  );
};
