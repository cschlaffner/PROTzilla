import { InputContainerProps } from "../input-container";
import type { UIStateProps } from "@protzilla/utils";

export interface DropdownInputFieldProps extends InputContainerProps, UIStateProps {
  options: { label: string; value: string }[];
  value?: string | null;
  onChange: (value: string | null) => void;
}
