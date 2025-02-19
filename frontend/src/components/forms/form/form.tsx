import React, { useState } from "react";
import { FormProps } from "./form.props";
import { styled } from "styled-components";
import { color, fontSize, size, spacing } from "../../../theme";

import { Text } from "../../text";
import { TextInputField } from "../../input-fields/text-input-field";
import { NumberInputField } from "../../input-fields/number-input-field";
import { SearchInputField } from "../../input-fields/search-input-field";
import { RadioSelectInputField } from "../../input-fields/radio-select-input-field";
import { CheckboxSelectInputField } from "../../input-fields/checkbox-select-input-field";
import { DropdownInputField } from "../../input-fields/dropdown-input-field";
import { MultiSelectInputField } from "../../input-fields/multi-select-input-field";
import { Button } from "../../button";

const StyledForm = styled.div`
  width: 100%;
  max-width: ${size("inputFieldsMaxWidth")};
`;

const FormLabel = styled(Text)`
  color: ${color("gray50")};
  font-size: ${fontSize("default")};
`;

const StyledSubmitDiv = styled.div`
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: ${spacing("small")};
`;

const SubmitButton = styled(Button)`
  color: ${color("gray50")};
  font-size: ${fontSize("default")};
`;

const ChangeIndicator = styled.div`
  color: ${color("red")};
  font-size: ${fontSize("default")};
`;

export const Form: React.FC<FormProps> = ({ formData, onChange, onFirstChange}) => {
  const [formValues, setFormValues] = useState<{ [key: string]: any }>({});
  const [submittedValues, setSubmittedValues] = useState<{ [key: string]: any }>({});
  const [isChanged, setIsChanged] = useState(false);
  const [firstChangeTriggered, setFirstChangeTriggered] = useState(false);

  const handleChange = (id: string, value: any) => {
    setFormValues((prevValues) => {
      const newValues = { ...prevValues, [id]: value };
      const hasChanges = JSON.stringify(newValues) !== JSON.stringify(submittedValues);

      if (!formData.submit) {
        onChange(newValues);
      } else {
        setIsChanged(hasChanges);
        
        if (!firstChangeTriggered && hasChanges) {
          onFirstChange?.(true);
          setFirstChangeTriggered(true);
        }
      }

      return newValues;
    });
  };

  const handleSubmit = () => {
    onChange(formValues);
    setSubmittedValues(formValues); 
    setIsChanged(false);
    setFirstChangeTriggered(false);
  };

  return (
    <StyledForm>
      <FormLabel>{formData.label}</FormLabel>
      {formData.input_fields.map((inputField) => (
        <InputField
          type={inputField.type}
          id={inputField.id}
          onChange={handleChange}
          {...inputField.props}
        />
      ))}
      {formData.submit && (
        <StyledSubmitDiv>
          {isChanged && <ChangeIndicator>New changes can be submitted</ChangeIndicator>}
          <SubmitButton text="Submit" onClick={handleSubmit} isDisabled={!isChanged} />
        </StyledSubmitDiv>
      )}
    </StyledForm>
  );
};

interface InputFieldProps {
  type: string;
  id: string;
  onChange: (id: string, value: any) => void;
  options?: { label: string; value: string }[];
  [key: string]: any;
}

const InputField: React.FC<InputFieldProps> = ({
  type,
  id,
  onChange,
  options,
  ...props
}) => {
  const handleInputChange = (value: any) => {
    onChange(id, value);
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
        <RadioSelectInputField
          onChange={handleInputChange}
          options={options ?? []}
          {...props}
        />
      );
    case "checkbox-select":
      return (
        <CheckboxSelectInputField
          onChange={handleInputChange}
          options={options ?? []}
          {...props}
        />
      );
    case "dropdown":
      return (
        <DropdownInputField
          onChange={handleInputChange}
          options={options ?? []}
          {...props}
        />
      );
    case "multi-select":
      return (
        <MultiSelectInputField
          onChange={handleInputChange}
          options={options ?? []}
          {...props}
        />
      );
    default:
      return null;
  }
};
