import type { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "@protzilla/core";

export interface SearchInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  style?: React.CSSProperties;
}
