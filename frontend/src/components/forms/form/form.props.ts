import { CheckboxSelectInputFieldProps } from "../../input-fields/checkbox-select-input-field";
import { DropdownInputFieldProps } from "../../input-fields/dropdown-input-field";
import { MultiSelectInputFieldProps } from "../../input-fields/multi-select-input-field";
import { NumberInputFieldProps } from "../../input-fields/number-input-field";
import { RadioSelectInputFieldProps } from "../../input-fields/radio-select-input-field";
import { SearchInputFieldProps } from "../../input-fields/search-input-field";
import { TextInputFieldProps } from "../../input-fields/text-input-field";

export interface FormProps {
  formData: FormData;
}

export interface FormData {
  label: string;
  onChange: string;
  confirm: boolean;
  input_fields: InputField[];
}

export type InputField = 
  | { type: 'text'; id: string; props: Omit<TextInputFieldProps, "onChange"> }
  | { type: 'number'; id: string; props: Omit<NumberInputFieldProps, "onChange"> }
  | { type: 'search'; id: string; props: Omit<SearchInputFieldProps, "onChange"> }
  | { type: 'radio-select'; id: string; props: Omit<RadioSelectInputFieldProps, "onChange"> }
  | { type: 'checkbox-select'; id: string; props: Omit<CheckboxSelectInputFieldProps, "onChange"> }
  | { type: 'multi-select'; id: string; props: Omit<MultiSelectInputFieldProps, "onChange"> }
  | { type: 'dropdown'; id: string; props: Omit<DropdownInputFieldProps, "onChange"> };

export type InputFieldProps =
  | TextInputFieldProps
  | NumberInputFieldProps
  | SearchInputFieldProps
  | RadioSelectInputFieldProps
  | CheckboxSelectInputFieldProps
  | MultiSelectInputFieldProps
  | DropdownInputFieldProps;