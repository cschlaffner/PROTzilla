import type { UIStateProps } from "../../../utils";
import { FrameInputFieldProps } from "../frame-input-field";

export interface NumberInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  value?: number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  isInteger?: boolean;
  onChange: (value: number) => void;
}
