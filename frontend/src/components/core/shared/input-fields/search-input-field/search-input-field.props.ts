import { InputContainerProps } from "../input-container";
import type { UIStateProps } from "@protzilla/utils";

export interface SearchInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  style?: React.CSSProperties;
}
