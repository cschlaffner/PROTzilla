import { InputContainerProps } from "@protzilla/core";
import type { UIStateProps } from "@protzilla/utils";

export interface TextInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  characterLimit?: number;
}
