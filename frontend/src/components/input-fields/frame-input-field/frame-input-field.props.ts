import type { UIStateProps } from "../../types";

export interface FrameInputFieldProps extends UIStateProps {
  label?: string;
  labelPosition?: "top" | "side";
  subscript?: string;
  optional?: boolean;
  children?: React.ReactNode;
  inlinePrefix?: React.ReactNode;
  inlineSuffix?: React.ReactNode;
  separatePrefix?: React.ReactNode;
  separateSuffix?: React.ReactNode;
  smallBorder?: boolean;
  smallFrame?: boolean;
}
