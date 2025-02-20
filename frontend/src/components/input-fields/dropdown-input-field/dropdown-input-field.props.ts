import type { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface DropdownInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
  options: { label: string; value: string }[];
  defaultValue?: { label: string; value: string };
  onChange: (value: string) => void;
}

export interface DropdownInputFieldRef {
  getValue: () => string;
  setValue: (value: string) => void;
}
