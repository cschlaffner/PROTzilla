import type { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "@protzilla/core";

export interface TextInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  characterLimit?: number;
}
