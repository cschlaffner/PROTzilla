import type { UIStateProps } from "../../types";
import { TextInputFieldProps } from "../text-input-field";


export interface DropdownInputFieldProps
    extends Omit<TextInputFieldProps, "onSelect">, UIStateProps {
    options: string[];
    value?: string;
    defaultValue?: string;
    onSelect: (value: string) => void;
}
