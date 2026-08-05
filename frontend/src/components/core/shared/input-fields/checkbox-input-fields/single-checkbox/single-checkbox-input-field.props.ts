import { InputContainerProps } from "../../input-container";

export interface SingleCheckboxInputFieldProps extends InputContainerProps {
  value?: boolean;
  text?: string;
  onChange: (value: boolean) => void;
  id?: string;
}
