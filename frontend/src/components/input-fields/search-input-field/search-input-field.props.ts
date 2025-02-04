import type {
  UIStateProps,
} from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";

export interface SearchInputFieldProps
  extends Omit<
    React.InputHTMLAttributes<HTMLInputElement>,
     "onChange" | "children" | "value"
  >,
  FrameInputFieldProps,
  UIStateProps {
  placeholder?: string;
  onChange?: (value: string) => void;
}