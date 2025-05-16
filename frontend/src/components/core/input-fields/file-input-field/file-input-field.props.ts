import { InputContainerProps } from "@protzilla/core";
import type { UIStateProps } from "@protzilla/utils";

export interface FileInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string | null; // The filename
  placeholder?: string;
  onChange: (value: string) => void;
}
