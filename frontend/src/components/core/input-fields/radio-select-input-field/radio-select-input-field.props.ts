import { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "@protzilla/core";

export interface RadioSelectInputFieldProps
  extends Omit<InputContainerProps, "inlinePrefix" | "inlineSuffix">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string;
  onChange: (value: string) => void;
}
