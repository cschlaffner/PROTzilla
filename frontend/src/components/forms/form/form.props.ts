export interface FormProps {
  formData: FormData;
}

export interface FormData {
  label: string;
  onChange: string;
  confirm: boolean;
  input_fields: {
    type: string;
    id: string;
    props: {
      label: string;
      defaultValues: string | number;
    };
  }[];
}
