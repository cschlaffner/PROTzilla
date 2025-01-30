import type {
    I18nComponents,
    I18nData,
    I18nLabelProps,
    I18nPlaceholderProps,
    UIStateProps,
  } from "../types";

export interface NumberFieldProps
    extends Omit<
      React.InputHTMLAttributes<HTMLInputElement>,
      "defaultValue" | "value"
    >,
    I18nLabelProps,
    I18nPlaceholderProps,
    UIStateProps {
        defaultValue?: string;
        value?: string;
        placeholder?: string;
        min?: number;
        max?: number;
        step?: number;
        onChange?: (value: number) => void;
}