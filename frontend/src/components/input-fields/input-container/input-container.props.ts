import type { UIStateProps } from "../../types";

export interface InputContainerProps extends UIStateProps {
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
