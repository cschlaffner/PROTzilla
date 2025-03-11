import type { UIStateProps } from "../../types";
import { InputContainerProps } from "../input-container";

export interface FileInputFieldProps extends InputContainerProps, UIStateProps {
  value?: File | null;
  placeholder?: string;
  onChange: (value: File | null) => void;
}
