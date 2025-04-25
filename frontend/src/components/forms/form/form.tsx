import React, { useEffect, useState } from "react";
import { styled } from "styled-components";

import { FormProps, InputFieldProps, InputValueType } from "./form.props";
import { color, fontSize, size, spacing } from "../../../theme";
import { Button } from "../../button";
import { CheckboxSelectInputField } from "../../input-fields/checkbox-input-fields/checkbox-select-input-field";
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

const ChangeIndicator = styled.div`
  color: ${color("red")};
  font-size: ${fontSize("default")};
`;

export const Form: React.FC<FormProps> = ({
  formData,
  onChange,
  onFormTouched,
}) => {
  const [formValues, setFormValues] = useState<Record<string, InputValueType>>(
    {},
  );
  const [submittedValues, setSubmittedValues] = useState<
    Record<string, InputValueType>
  >({});
  const [isChanged, setIsChanged] = useState(false);
  const [hasformTouchedTriggered, setHasFormTouchedTriggered] = useState(false);

  useEffect(() => {
    setFormValues({});
  }, [formData]);

  const handleChange = (name: string, value: InputValueType) => {
    if (formValues[name] === value) return;

    const newValues = { ...formValues, [name]: value };
    const hasChanges =
      JSON.stringify(newValues) !== JSON.stringify(submittedValues);

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
        <InputField
          key={i.toString()}
          onChange={handleChange}
          {...inputField}
        />
      ))}
      {!formData.isAutoSubmit && (
        <StyledSubmitDiv>
          {isChanged && (
            <ChangeIndicator>New changes can be submitted</ChangeIndicator>
          )}
          <SubmitButton
            text="Submit"
            onClick={handleSubmit}
            isDisabled={!isChanged}
          />
        </StyledSubmitDiv>
      )}
    </StyledForm>
  );
};

const InputField: React.FC<InputFieldProps> = ({
  type,
  name,
  onChange,
  options,
  isVisible,
  ...props
}) => {
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
    case "file":
      return <FileInputField onChange={handleInputChange} {...props} />;
    default:
      return null;
  }
  //}
};
