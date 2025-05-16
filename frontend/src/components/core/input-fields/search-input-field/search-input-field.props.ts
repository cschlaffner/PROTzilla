import { InputContainerProps } from "@protzilla/core";
import type { UIStateProps } from "@protzilla/utils";

export interface SearchInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  style?: React.CSSProperties;
}
