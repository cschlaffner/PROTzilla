import { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface CheckboxSelectInputFieldProps
  extends Omit<FrameInputFieldProps, "inlinePrefix" | "inlineSuffix">,
    UIStateProps {
  options: { label: string; value: string }[];
  defaultOptions?: string[];
  onChange: (value: string[]) => void;
}
