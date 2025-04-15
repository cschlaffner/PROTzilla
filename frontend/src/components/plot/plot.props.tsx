import { Data, Layout } from "plotly.js";

export interface PlotProps {
  data: Data[];
  layout: Partial<Layout>;
  styleProps?: React.CSSProperties;
  divId?: string;
}
