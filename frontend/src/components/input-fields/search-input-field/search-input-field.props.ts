import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface SearchInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  defaultValue?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  style?: React.CSSProperties;
}
