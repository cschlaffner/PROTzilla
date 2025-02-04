import type { UIStateProps } from "../../types";

export interface FrameInputFieldProps extends UIStateProps {
  label?: string;
  labelPosition?: "top" | "side";
  subscript?: string;
  children: React.ReactNode;
  inlinePrefix?: React.ReactNode;
  inlineSuffix?: React.ReactNode;
  separatePrefix?: React.ReactNode;
  separateSuffix?: React.ReactNode;
}
