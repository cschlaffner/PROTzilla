import Plot from "react-plotly.js";

import { PlotProps } from "./plot.props";
import { SectionTitle } from "../section-title";

export const PlotComponent: React.FC<PlotProps> = ({ data, layout }) => {
  return (
    <div style={{ width: "100%", height: "100%", flexGrow: 1, minHeight: 0 }}>
      {data && data.length > 0 ? (
        <Plot
          data={data}
          layout={{ ...layout, autosize: true }}
          style={{ width: "100%", height: "100%" }}
          useResizeHandler={true}
        />
      ) : (
        <SectionTitle
          baseComponent={"h4"}
          description={"No plot available for this step."}
        />
      )}
    </div>
  );
};
