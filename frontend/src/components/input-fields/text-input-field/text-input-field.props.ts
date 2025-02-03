import type {
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps,
} from "../../types";

export interface TextInputFieldProps
  extends Omit<
    React.InputHTMLAttributes<HTMLInputElement>,
    "defaultValue" | "value" | "onChange"
  >,
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps {
  label?: string,
  value?: string;
  defaultValue?: string;
  placeholder?: string;
  onChange?: (value: string) => void;
}