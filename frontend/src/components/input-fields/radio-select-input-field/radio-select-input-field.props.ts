import { UIStateProps } from "../../../utils";
import { InputContainerProps } from "../input-container";

export interface RadioSelectInputFieldProps
  extends Omit<InputContainerProps, "inlinePrefix" | "inlineSuffix">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string;
  onChange: (value: string) => void;
}
