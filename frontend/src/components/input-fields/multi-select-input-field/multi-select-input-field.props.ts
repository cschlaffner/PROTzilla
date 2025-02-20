import { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface MultiSelectInputFieldProps
  extends Omit<FrameInputFieldProps, "onChange">,
    UIStateProps {
  options: { label: string; value: string }[];
  selectedOptions?: string[];
  onChange: (selectedValues: string[]) => void;
}

export interface MultiSelectInputFieldRef {
  getValue: () => string[];
  setValue: (values: string[]) => void;
}
