import type {
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps,
} from "../../types";

export interface NumberInputFieldProps
  extends Omit<
    React.InputHTMLAttributes<HTMLInputElement>,
    "defaultValue" | "value" | "onChange"
  >,
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps {
  label?: string,
  value?: number;
  defaultValue?: number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  onChange?: (value: number) => void;
}