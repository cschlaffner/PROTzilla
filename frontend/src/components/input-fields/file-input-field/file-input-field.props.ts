import type { UIStateProps } from "@protzilla/utils";
import { InputContainerProps } from "../input-container";

export interface FileInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string | null; // The filename
  placeholder?: string;
  onChange: (value: string) => void;
}
