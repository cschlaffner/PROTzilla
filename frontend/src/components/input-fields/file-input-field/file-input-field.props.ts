import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface FileInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  // defaultValue?: string;
  // placeholder?: string;
  onChange: (value: string) => void;
}

export interface FileInputFieldRef {
  // getValue: () => string;
  // setValue: (value: string) => void;
}
