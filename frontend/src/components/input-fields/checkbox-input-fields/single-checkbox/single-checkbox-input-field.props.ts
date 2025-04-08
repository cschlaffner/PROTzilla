import { FrameInputFieldProps } from "../../frame-input-field";

export interface SingleCheckboxInputFieldProps extends FrameInputFieldProps {
  value: boolean;
  text: string;
  onChange: (value: boolean) => void;
}
