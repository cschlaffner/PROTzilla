import { RequestData, RunData, StepID, StepStatus } from "@protzilla/utils";

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

export interface BackendFormProps {
  runName: string;
  buttonText: string;
  previousStepCalculationStatus: StepStatus | undefined;
  currentStepCalculationStatus: StepStatus | undefined;
  current_step_id: StepID;
  isLastStep: boolean;
  onNext: () => void;
  onChange: () => void;
  onSubmit: (request: RequestData) => void;
  runData: RunData;
}

export interface BackendFormData {
  label: string;
  isAutoSubmit: boolean;
  hasChangeIndicator: boolean;
  input_fields: BackendInputField[];
}

export interface NamedHandle {
  name: string;
  type: string;
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
  | {
      type: "named-handles";
      name: string;
      label: string;
      isVisible: boolean;
      options: { label: string; value: string }[];
      value: NamedHandle[];
    }
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

export type BackendInputValueType = ExtractValueType<InputFields> | NamedHandle[];

export interface BackendInputFieldProps {
  type: string;
  name: string;
  onChange: (name: string, value: BackendInputValueType) => void;
  options?: { label: string; value: string }[];
  label?: string;
  value?: BackendInputValueType;
  key: string;
  isVisible?: boolean;
}
