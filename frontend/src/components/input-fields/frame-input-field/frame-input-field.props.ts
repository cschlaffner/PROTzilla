import type { UIStateProps } from "../../types";

export interface FrameInputFieldProps extends UIStateProps {
  children?: React.ReactNode;
  label?: string;
  labelPosition?: "top" | "side";
  optional?: boolean;
  subscript?: string;
  inlinePrefix?: React.ReactNode;
  inlineSuffix?: React.ReactNode;
  separatePrefix?: React.ReactNode;
  separateSuffix?: React.ReactNode;
  smallBorder?: boolean;
  smallFrame?: boolean;
}
