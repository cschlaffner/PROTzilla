import { UIStateProps } from "../../../../utils";
import { FrameInputFieldProps } from "../../frame-input-field";

export interface CheckboxSelectInputFieldProps
  extends Omit<FrameInputFieldProps, "inlinePrefix" | "inlineSuffix">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string[];
  onChange: (value: string[]) => void;
}
