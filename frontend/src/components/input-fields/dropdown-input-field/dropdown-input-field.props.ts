import type { UIStateProps } from "../../types";
import { InputContainerProps } from "../input-container";

export interface DropdownInputFieldProps
  extends InputContainerProps,
    UIStateProps {
  options: { label: string; value: string }[];
  value?: string;
  onChange: (value: string) => void;
}
