import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface DropdownInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  options: { label: string; value: string }[];
  defaultValue?: string;
  onChange: (value: string) => void;
}
