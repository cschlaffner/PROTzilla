import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface DropdownInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  options: string[];
  defaultValue?: string;
  onClick: (value: string) => void;
}
