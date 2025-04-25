import { CheckboxSelectInputFieldProps } from "../../input-fields/checkbox-input-fields/checkbox-select-input-field";
import { SingleCheckboxInputFieldProps } from "../../input-fields/checkbox-input-fields/single-checkbox";
import { DropdownInputFieldProps } from "../../input-fields/dropdown-input-field";
import { FileInputFieldProps } from "../../input-fields/file-input-field";
import { MultiSelectInputFieldProps } from "../../input-fields/multi-select-input-field";
import { NumberInputFieldProps } from "../../input-fields/number-input-field";
import { RadioSelectInputFieldProps } from "../../input-fields/radio-select-input-field";
import { SearchInputFieldProps } from "../../input-fields/search-input-field";
import { TextInputFieldProps } from "../../input-fields/text-input-field";

export interface FormProps {
  formData: FormData;
  onChange: (data: Record<string, InputValueType>) => void;
  onFormTouched?: (hasChanged: boolean) => void;
}

export interface FormData {
  label: string;
  isAutoSubmit: boolean;
  hasChangeIndicator: boolean;
  input_fields: InputField[];
}

export type InputField =
  | ({ 
      type: "text"; 
      name: string; 
      isVisible: boolean 
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
      isVisible:boolean;
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

export type InputValueType = ExtractValueType<InputFields>;

export interface InputFieldProps {
  type: string;
  name: string;
  onChange: (name: string, value: InputValueType) => void;
  options?: { label: string; value: string }[];
  key: string;
  isVisible?: boolean;
}
