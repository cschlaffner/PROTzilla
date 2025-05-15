import type { UIStateProps } from "../../types";
import { InputContainerProps } from "../input-container";

export interface TextInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  characterLimit?: number;
}
