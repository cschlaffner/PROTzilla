import { InputContainerProps } from "../input-container";
import type { UIStateProps } from "@protzilla/utils";

export interface FileInputFieldProps extends InputContainerProps, UIStateProps {
  value?: string | null; // The filename
  placeholder?: string;
  onChange: (value: string) => void;
}
