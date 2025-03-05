import { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface RadioSelectInputFieldProps
  extends Omit<FrameInputFieldProps, "inlinePrefix" | "inlineSuffix">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string;
  onChange: (value: string) => void;
}
