import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface FileInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  defaultValue?: File | null;
  placeholder?: string;
  onChange: (value: File) => void;
}

export interface FileInputFieldRef {
  getValue: () => File | null;
  setValue: (file: File) => void;
}