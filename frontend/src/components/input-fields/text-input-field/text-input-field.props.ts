import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface TextInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
}
