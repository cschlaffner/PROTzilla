import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface NumberInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  defaultValue?: number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  onChange: (value: number) => void;
}

export interface NumberInputFieldRef {
  getValue: () => number | null;
  setValue: (value: number) => void;
}
