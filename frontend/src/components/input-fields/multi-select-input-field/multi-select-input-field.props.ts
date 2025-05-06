import { UIStateProps } from "../../../utils";
import { FrameInputFieldProps } from "../frame-input-field";

export interface MultiSelectInputFieldProps
  extends Omit<FrameInputFieldProps, "onChange">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string[];
  onChange: (selectedValues: string[]) => void;
}
