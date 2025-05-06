import type { UIStateProps } from "../../../utils";
import { FrameInputFieldProps } from "../frame-input-field";

export interface DropdownInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string;
  onChange: (value: string) => void;
}
