import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface FileInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  value?: File | null;
  placeholder?: string;
  onChange: (value: File | null ) => void;
}