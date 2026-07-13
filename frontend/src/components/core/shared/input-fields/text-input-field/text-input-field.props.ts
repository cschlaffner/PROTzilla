import type { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "../input-container";

export interface TextInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  characterLimit?: number;
  rows?: number;
  isCodeEditor?: boolean;
}
