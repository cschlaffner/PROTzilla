import { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface MultiSelectInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  options: { label: string; value: string }[];
  selectedOptions?: string[];
  onChange: (value: string) => void;
}
