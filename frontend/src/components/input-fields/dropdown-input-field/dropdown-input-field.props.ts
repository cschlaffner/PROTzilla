import type { UIStateProps } from "../../../utils";
import { InputContainerProps } from "../input-container";

export interface DropdownInputFieldProps extends InputContainerProps, UIStateProps {
  options: { label: string; value: string }[];
  value?: string | null;
  onChange: (value: string | null) => void;
}
