import type { UIStateProps } from "../../../utils";
import { FrameInputFieldProps } from "../frame-input-field";

export interface TextInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
}
