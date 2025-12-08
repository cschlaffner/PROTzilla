import {
  CheckboxSelectInputFieldProps,
  DropdownInputFieldProps,
  FileInputFieldProps,
  HeaderInfoFieldProps,
  InfoFieldProps,
  MultiSelectInputFieldProps,
  NumberInputFieldProps,
  RadioSelectInputFieldProps,
  SearchInputFieldProps,
  SingleCheckboxInputFieldProps,
  TextInputFieldProps,
} from "../../input-fields";

export interface FormProps {
  formData: FormData;
  onChange: (data: Record<string, InputValueType>) => void;
  onFormTouched?: (hasChanged: boolean) => void;
}

export interface FormData {
  label: string;
  labelSubmitButton?: string;
  isAutoSubmit: boolean;
  hasChangeIndicator: boolean;
  input_fields: InputField[];
}

export type InputField =
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
    } & Omit<FileInputFieldProps, "onChange">)
  | ({
      type: "info-field";
      name: string;
      isVisible: boolean;
    } & Omit<InfoFieldProps, "onChange">)
  | ({
      type: "header-info-field";
      name: string;
      isVisible: boolean;
    } & Omit<HeaderInfoFieldProps, "onChange">);

type InputFields =
  | TextInputFieldProps
  | NumberInputFieldProps
  | SearchInputFieldProps
  | RadioSelectInputFieldProps
  | CheckboxSelectInputFieldProps
  | SingleCheckboxInputFieldProps
  | MultiSelectInputFieldProps
  | DropdownInputFieldProps
  | FileInputFieldProps
  | InfoFieldProps
  | HeaderInfoFieldProps;

type ExtractValueType<T> = T extends { value?: infer U } ? U : never;

export type InputValueType = ExtractValueType<InputFields>;

export interface InputFieldProps {
  type: string;
  name: string;
  onChange: (name: string, value: InputValueType) => void;
  options?: { label: string; value: string }[];
  key: string;
  isVisible?: boolean;
}
