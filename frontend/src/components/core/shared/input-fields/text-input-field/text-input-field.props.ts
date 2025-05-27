import { InputContainerProps } from "../input-container";
import type { UIStateProps } from "@protzilla/utils";

export interface TextInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  characterLimit?: number;
}
