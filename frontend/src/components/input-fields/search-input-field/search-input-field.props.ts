import type { UIStateProps } from "../../../utils";
import { InputContainerProps } from "../input-container";

export interface SearchInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  style?: React.CSSProperties;
}
