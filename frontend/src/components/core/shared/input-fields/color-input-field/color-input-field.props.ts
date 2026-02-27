import type { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "../input-container";

export interface ColorInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  onChange: (value: string) => void;
  subscript?: string;
  isSmall?: boolean;
}
