import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface FileInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  value?: string | null; // The filename
  placeholder?: string;
  onChange: (value: string) => void;
}
