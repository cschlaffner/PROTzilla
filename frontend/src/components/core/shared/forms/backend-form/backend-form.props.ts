import {
  CheckboxSelectInputFieldProps,
  DropdownInputFieldProps,
  FileInputFieldProps,
  MultiSelectInputFieldProps,
  NumberInputFieldProps,
  RadioSelectInputFieldProps,
  SearchInputFieldProps,
  SingleCheckboxInputFieldProps,
  TextInputFieldProps,
} from "../../input-fields";
import { RequestData, StepStatus } from "@protzilla/utils";

export interface BackendFormProps {
  runName: string;
  buttonText: string;
  previousStepCalculationStatus: StepStatus | undefined;
  currentStepCalculationStatus: StepStatus | undefined;
  current_step_index: number;
  onNext: () => void;
  onChange: () => void;
  onSubmit: (request: RequestData) => void;
}

export interface BackendFormData {
  label: string;
  isAutoSubmit: boolean;
  hasChangeIndicator: boolean;
  input_fields: BackendInputField[];
}

export type BackendInputField =
  | ({
      type: "text";
      name: string;
      isVisible: boolean;
    } & Omit<TextInputFieldProps, "onChange">)
  | ({
      type: "number";
      name: string;
      isVisible: boolean;
    } & Omit<NumberInputFieldProps, "onChange">)
  | ({
      type: "search";
      name: string;
      isVisible: boolean;
    } & Omit<SearchInputFieldProps, "onChange">)
  | ({
      type: "radio-select";
      name: string;
      isVisible: boolean;
    } & Omit<RadioSelectInputFieldProps, "onChange">)
  | ({
      type: "checkbox-select";
      name: string;
      isVisible: boolean;
    } & Omit<CheckboxSelectInputFieldProps, "onChange">)
  | ({
      type: "single-checkbox";
      name: string;
      isVisible: boolean;
    } & Omit<SingleCheckboxInputFieldProps, "onChange">)
  | ({
      type: "multi-select";
      name: string;
      isVisible: boolean;
    } & Omit<MultiSelectInputFieldProps, "onChange">)
  | ({
      type: "dropdown";
      name: string;
      isVisible: boolean;
    } & Omit<DropdownInputFieldProps, "onChange">)
  | ({
      type: "file";
      name: string;
      isVisible: boolean;
    } & Omit<FileInputFieldProps, "onChange">);

type InputFields =
  | TextInputFieldProps
  | NumberInputFieldProps
  | SearchInputFieldProps
  | RadioSelectInputFieldProps
  | CheckboxSelectInputFieldProps
  | SingleCheckboxInputFieldProps
  | MultiSelectInputFieldProps
  | DropdownInputFieldProps
  | FileInputFieldProps;

type ExtractValueType<T> = T extends { value?: infer U } ? U : never;

export type BackendInputValueType = ExtractValueType<InputFields>;

export interface BackendInputFieldProps {
  type: string;
  name: string;
  onChange: (name: string, value: BackendInputValueType) => void;
  options?: { label: string; value: string }[];
  key: string;
  isVisible?: boolean;
}
