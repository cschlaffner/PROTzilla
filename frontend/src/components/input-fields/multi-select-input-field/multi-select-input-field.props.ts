import { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface MultiSelectInputFieldProps
  extends Omit<FrameInputFieldProps, "onChange">,
    UIStateProps {
  options: { label: string; value: string }[];
  defaultOptions?: string[];
  onChange: (selectedValues: string[]) => void;
}
