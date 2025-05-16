import type { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "@protzilla/core";

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
