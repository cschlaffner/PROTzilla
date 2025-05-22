import {
  CheckboxSelectInputField,
  DropdownInputField,
  FileInputField,
  MultiSelectInputField,
  NumberInputField,
  RadioSelectInputField,
  SearchInputField,
  SingleCheckboxInputField,
  SubmitButton,
  TextInputField,
} from "@protzilla/core";
import { H3 } from "@protzilla/core/shared";
import { color, fontSize, size, spacing } from "@protzilla/theme";
import React, { memo, useState } from "react";
import { styled } from "styled-components";

import { FormProps, InputFieldProps, InputValueType } from "./form.props";

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

const ChangeIndicator = styled.div`
  color: ${color("red")};
  font-size: ${fontSize("default")};
`;

export const Form: React.FC<FormProps> = ({ formData, onChange, onFormTouched }) => {
  const [formValues, setFormValues] = useState<Record<string, InputValueType>>({});
  const [submittedValues, setSubmittedValues] = useState<Record<string, InputValueType>>({});
  const [isChanged, setIsChanged] = useState(false);
  const [hasformTouchedTriggered, setHasFormTouchedTriggered] = useState(false);

  const handleChange = (name: string, value: InputValueType) => {
    if (formValues[name] === value) return;

    const newValues = { ...formValues, [name]: value };
    const hasChanges = JSON.stringify(newValues) !== JSON.stringify(submittedValues);

    const isFirstEntryForId = !(name in formValues);
    if (isFirstEntryForId) {
      setFormValues(newValues);
    }

    if (formData.isAutoSubmit) {
      onChange(newValues);
    } else {
      setIsChanged(hasChanges);

      if (hasChanges) {
        if (!hasformTouchedTriggered) {
          onFormTouched?.(true);
          setHasFormTouchedTriggered(true);
        }
      } else {
        onFormTouched?.(false);
        setHasFormTouchedTriggered(false);
      }
    }
    setFormValues(newValues);
  };

  const handleSubmit = () => {
    onChange(formValues);
    setSubmittedValues(formValues);
    setIsChanged(false);
    setHasFormTouchedTriggered(false);
  };

  return (
    <StyledForm>
      <H3>{formData.label}</H3>
      {formData.input_fields.map((inputField, i) => (
        <InputField key={i.toString()} onChange={handleChange} {...inputField} />
      ))}
      {!formData.isAutoSubmit && (
        <StyledSubmitDiv>
          {isChanged && formData.hasChangeIndicator && (
            <ChangeIndicator>New changes can be submitted</ChangeIndicator>
          )}
          <SubmitButton
            text="Submit"
            onClick={handleSubmit}
            isDisabled={!isChanged && formData.hasChangeIndicator}
          />
        </StyledSubmitDiv>
      )}
    </StyledForm>
  );
};

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

  if (isVisible === false) {
    return null;
  }

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
