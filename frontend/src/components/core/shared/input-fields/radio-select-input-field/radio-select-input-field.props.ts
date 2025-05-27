import { InputContainerProps } from "../input-container";
import { UIStateProps } from "@protzilla/utils";

export interface RadioSelectInputFieldProps
  extends Omit<InputContainerProps, "inlinePrefix" | "inlineSuffix">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string;
  onChange: (value: string) => void;
}
