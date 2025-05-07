import type { UIStateProps } from "../../types";
import { InputContainerProps } from "../input-container";

export interface NumberInputFieldProps
  extends InputContainerProps,
    UIStateProps {
  value?: number;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  hasStepButtons?: boolean;
  isInteger?: boolean;
  onChange: (value: number) => void;
}
