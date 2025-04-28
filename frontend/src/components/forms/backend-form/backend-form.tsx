import React, { memo, useCallback, useEffect, useState } from "react";
import { styled } from "styled-components";

import { BackendFormProps, FormData, InputFieldProps, InputValueType } from "./backend-form.props";
import { color, fontSize, size, spacing } from "../../../theme";
import { callApiWithParameters } from "../../../utils/api-call";
import { Button } from "../../button";
import { CheckboxSelectInputField } from "../../input-fields/checkbox-input-fields/checkbox-select-input-field";
import { SingleCheckboxInputField } from "../../input-fields/checkbox-input-fields/single-checkbox";
import { DropdownInputField } from "../../input-fields/dropdown-input-field";
import { FileInputField } from "../../input-fields/file-input-field";
import { MultiSelectInputField } from "../../input-fields/multi-select-input-field";
import { NumberInputField } from "../../input-fields/number-input-field";
import { RadioSelectInputField } from "../../input-fields/radio-select-input-field";
import { SearchInputField } from "../../input-fields/search-input-field";
import { TextInputField } from "../../input-fields/text-input-field";
import { H3 } from "../../text";

const StyledForm = styled.div`
  max-width: ${size("inputFieldsMaxWidth")};
`;

const StyledSubmitDiv = styled.div`
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: ${spacing("small")};
  padding-top: ${spacing("small")};
`;

const SubmitButton = styled(Button)`
  color: ${color("gray50")};
  font-size: ${fontSize("default")};
`;

export const BackendForm: React.FC<BackendFormProps> = memo(function Form({
  runName,
  current_step_index,
  onSubmit,
  onChange,
}) {
  const [formData, setFormData] = useState<FormData>();

  useEffect(() => {
    void getStepForm();
  }, []);

  useEffect(() => {
    void getStepForm();
  }, [current_step_index]);

  const getStepForm = async (values: Record<string, InputValueType> = {}) => {
    const response = await callApiWithParameters("get_step_form/", {
      run_name: runName,
      data: values,
    });
    if (response) {
      const data = response.data;
      setFormData(data);
    }
  };

  const handleChange = useCallback(
    (name: string, value: InputValueType) => {
      void getStepForm({ [name]: value });
      onChange();
    },
    [getStepForm, onChange],
  );

  const handleSubmit = async () => {
    const response = await callApiWithParameters("calculate_step/", {
      run_name: runName,
    });
    if (response) {
      console.log("response", response.data);
      onSubmit(response.data);
    }
  };

  return (
    <>
      {formData && (
        <StyledForm>
          <H3>{formData.label}</H3>
          {formData.input_fields.map((inputField) => (
            <InputField key={inputField.name} onChange={handleChange} {...inputField} />
          ))}
          <StyledSubmitDiv>
            <SubmitButton text="Calculate" onClick={handleSubmit} />
          </StyledSubmitDiv>
        </StyledForm>
      )}
    </>
  );
});

const InputField: React.FC<InputFieldProps> = memo(function InputField({
  type,
  name,
  onChange,
  options,
  isVisible,
  ...props
}) {
  const handleInputChange = (value: InputValueType) => {
    onChange(name, value);
  };

  switch (type) {
    case "text":
      return <TextInputField onChange={handleInputChange} {...props} />;
    case "number":
      return <NumberInputField onChange={handleInputChange} {...props} />;
    case "search":
      return <SearchInputField onChange={handleInputChange} {...props} />;
    case "radio-select":
      return (
        <RadioSelectInputField onChange={handleInputChange} options={options ?? []} {...props} />
      );
    case "checkbox-select":
      return (
        <CheckboxSelectInputField onChange={handleInputChange} options={options ?? []} {...props} />
      );
    case "single-checkbox":
      return <SingleCheckboxInputField onChange={handleInputChange} {...props} />;
    case "dropdown":
      return <DropdownInputField onChange={handleInputChange} options={options ?? []} {...props} />;
    case "multi-select":
      return (
        <MultiSelectInputField onChange={handleInputChange} options={options ?? []} {...props} />
      );
    case "file":
      return <FileInputField onChange={handleInputChange} {...props} />;
    default:
      return null;
  }
});
