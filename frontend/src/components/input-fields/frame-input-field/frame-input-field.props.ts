import type {
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps,
} from "../../types";

export interface FrameInputFieldProps
  extends 
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps {
  label?: string;
  children: React.ReactNode;
}