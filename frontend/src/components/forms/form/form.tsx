import React, { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import { FormProps } from "./form.props";
import { color, fontSize, fontWeight, size, spacing } from "../../../theme";
import { Button } from "../../button";
import { CheckboxSelectInputField } from "../../input-fields/checkbox-select-input-field";
import { DropdownInputField } from "../../input-fields/dropdown-input-field";
import { MultiSelectInputField } from "../../input-fields/multi-select-input-field";
import { NumberInputField } from "../../input-fields/number-input-field";
import { RadioSelectInputField } from "../../input-fields/radio-select-input-field";
import { SearchInputField } from "../../input-fields/search-input-field";
import { TextInputField } from "../../input-fields/text-input-field";
import { Text } from "../../text";

const StyledForm = styled.div`
  width: 100%;
  max-width: ${size("inputFieldsMaxWidth")};
`;

const FormLabel = styled(Text)`
  font-size: ${fontSize("h2")};
  line-height: ${fontSize("h2")};
  font-weight: ${fontWeight("bold")};
  color: ${color("primary")};
  padding-bottom: ${spacing("small")};
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

export const Form: React.FC<FormProps> = ({
  formData,
  onChange,
  onFormTouched,
}) => {
  const [formValues, setFormValues] = useState<Record<string, any>>({});
  const [submittedValues, setSubmittedValues] = useState<Record<string, any>>(
    {},
  );
  const [isChanged, setIsChanged] = useState(false);
  const [formTouchedTriggered, setFormTouchedTriggered] = useState(false);

  const inputRefs = useRef<{ [key: string]: any }>({});

  useEffect(() => {
    setTimeout(() => {
      const initialValues: Record<string, any> = {};
      Object.keys(inputRefs.current).forEach((key) => {
        if (inputRefs.current[key]?.getValue) {
          initialValues[key] = inputRefs.current[key].getValue();
        }
      });
      setFormValues(initialValues);
    }, 0);
  }, []);

  const handleChange = (id: string, value: any) => {
    setFormValues((prevValues) => {
      const newValues = { ...prevValues, [id]: value };
      const hasChanges =
        JSON.stringify(newValues) !== JSON.stringify(submittedValues);

      if (!formData.submit) {
        onChange(newValues);
      } else {
        setIsChanged(hasChanges);

        if (hasChanges) {
          if (!formTouchedTriggered) {
            onFormTouched?.(true);
            setFormTouchedTriggered(true);
          }
        } else {
          onFormTouched?.(false);
          setFormTouchedTriggered(false);
        }
      }

      return newValues;
    });
  };

  const handleSubmit = () => {
    onChange(formValues);
    setSubmittedValues(formValues);
    setIsChanged(false);
    setFormTouchedTriggered(false);
  };

  return (
    <StyledForm>
      <FormLabel as="h2">{formData.label}</FormLabel>
      {formData.input_fields.map((inputField) => (
        <InputField
          key={inputField.id}
          type={inputField.type}
          id={inputField.id}
          onChange={handleChange}
          ref={(el) => {
            if (el) inputRefs.current[inputField.id] = el;
          }}
          {...inputField.props}
        />
      ))}
      {formData.submit && (
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

interface InputFieldProps {
  type: string;
  id: string;
  onChange: (id: string, value: any) => void;
  options?: { label: string; value: string }[];
  [key: string]: any;
}

const InputField = React.forwardRef<any, InputFieldProps>(
  ({ type, id, onChange, options, ...props }, ref) => {
    const handleInputChange = (value: any) => {
      onChange(id, value);
    };

    switch (type) {
      case "text":
        return (
          <TextInputField ref={ref} onChange={handleInputChange} {...props} />
        );
      case "number":
        return (
          <NumberInputField ref={ref} onChange={handleInputChange} {...props} />
        );
      case "search":
        return (
          <SearchInputField ref={ref} onChange={handleInputChange} {...props} />
        );
      case "radio-select":
        return (
          <RadioSelectInputField
            ref={ref}
            onChange={handleInputChange}
            options={options ?? []}
            {...props}
          />
        );
      case "checkbox-select":
        return (
          <CheckboxSelectInputField
            ref={ref}
            onChange={handleInputChange}
            options={options ?? []}
            {...props}
          />
        );
      case "dropdown":
        return (
          <DropdownInputField
            ref={ref}
            onChange={handleInputChange}
            options={options ?? []}
            {...props}
          />
        );
      case "multi-select":
        return (
          <MultiSelectInputField
            ref={ref}
            onChange={handleInputChange}
            options={options ?? []}
            {...props}
          />
        );
      default:
        return null;
    }
  },
);
