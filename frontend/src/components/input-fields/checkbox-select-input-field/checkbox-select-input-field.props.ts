import { UIStateProps } from "../../types";
import { InputContainerProps } from "../input-container";

export interface CheckboxSelectInputFieldProps
  extends Omit<InputContainerProps, "inlinePrefix" | "inlineSuffix">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string[];
  onChange: (value: string[]) => void;
}
