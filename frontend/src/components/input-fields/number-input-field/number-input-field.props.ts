import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface NumberInputFieldProps
  extends Omit<
      React.InputHTMLAttributes<HTMLInputElement>,
      "defaultValue" | "value" | "onChange" | "children"
    >,
    FrameInputFieldProps,
    UIStateProps {
  value?: number;
  defaultValue?: number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  onChange?: (value: number) => void;
}
