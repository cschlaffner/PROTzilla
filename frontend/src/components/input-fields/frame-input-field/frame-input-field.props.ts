import type { UIStateProps } from "../../../utils";

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
  isSmall?: boolean;
}
