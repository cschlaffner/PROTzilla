import { InputContainerProps } from "@protzilla/core";

export interface SingleCheckboxInputFieldProps extends InputContainerProps {
  value?: boolean;
  text?: string;
  onChange: (value: boolean) => void;
}
