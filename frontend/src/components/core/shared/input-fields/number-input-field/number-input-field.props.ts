import { InputContainerProps } from "../input-container";
import type { UIStateProps } from "@protzilla/utils";

export interface NumberInputFieldProps extends InputContainerProps, UIStateProps {
  value?: number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  hasStepButtons?: boolean;
  isInteger?: boolean;
  onChange: (value: number) => void;
}
