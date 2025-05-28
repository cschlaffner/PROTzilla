import { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "../input-container";

export interface MultiSelectInputFieldProps
  extends Omit<InputContainerProps, "onChange">,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string[];
  onChange: (selectedValues: string[]) => void;
}
