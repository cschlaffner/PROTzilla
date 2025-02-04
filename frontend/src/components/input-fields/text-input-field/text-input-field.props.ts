import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface TextInputFieldProps
  extends Omit<
      React.InputHTMLAttributes<HTMLInputElement>,
      "defaultValue" | "value" | "onChange" | "children"
    >,
    FrameInputFieldProps,
    UIStateProps {
  value: string;
  defaultValue?: string;
  placeholder?: string;
  onChange?: (value: string) => void;
}
