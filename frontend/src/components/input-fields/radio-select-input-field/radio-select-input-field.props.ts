import { UIStateProps } from "../../types";
import { FrameInputFieldProps } from "../frame-input-field";


export interface RadioSelectInputFieldProps
  extends FrameInputFieldProps,
    UIStateProps {
    options: { label: string; value: string }[];
    selectedValue: string;
    onChange: (value: string) => void;
}
