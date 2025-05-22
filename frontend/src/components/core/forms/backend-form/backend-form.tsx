import { useNotification } from "@protzilla/app";
import {
  Button,
  CheckboxSelectInputField,
  DropdownInputField,
  FileInputField,
  MultiSelectInputField,
  NumberInputField,
  RadioSelectInputField,
  SearchInputField,
  SingleCheckboxInputField,
  TextInputField,
} from "@protzilla/core";
import { H3 } from "@protzilla/core/shared";
import { color, fontSize, size, spacing } from "@protzilla/theme";
import { callApiWithParameters } from "@protzilla/utils";
import React, { memo, useCallback, useEffect, useState } from "react";
import { styled } from "styled-components";

import {
  BackendFormData,
  BackendFormProps,
  BackendInputFieldProps,
  BackendInputValueType,
} from "./backend-form.props";

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
  buttonText,
  previousStepCalculationStatus,
  currentStepCalculationStatus,
  current_step_index,
  onNext,
  onSubmit,
  onChange,
}) {
  const notify = useNotification();

  const [BackendFormData, setBackendFormData] = useState<BackendFormData>();
  const [isloading, setLoading] = useState(false);

  const getStepForm = useCallback(
    async (values: Record<string, BackendInputValueType> = {}) => {
      const response = await callApiWithParameters("get_step_form/", {
        run_name: runName,
        data: values,
      });
      if (response) {
        const data = response.data;
        setBackendFormData(data);
      }
    },
    [runName],
  );

  useEffect(() => {
    void getStepForm();
  }, [current_step_index, getStepForm]);

  const handleChange = (name: string, value: BackendInputValueType) => {
    void getStepForm({ [name]: value });
    onChange();
  };

  const handleSubmit =
    currentStepCalculationStatus === "complete"
      ? onNext
      : async () => {
          setLoading(true);
          try {
            const response = await callApiWithParameters("calculate_step/", {
              run_name: runName,
            });
            if (response.success) {
              onSubmit(response.data);
            } else {
              const messages = response.message;
              if (Array.isArray(messages)) {
                messages.forEach((message) => {
                  notify({
                    title: "Error when calculating step",
                    type: "error",
                    isClosingAutomatically: false,
                    message: message,
                  });
                });
              } else {
                notify({
                  title: "Error when calculating step",
                  type: "error",
                  isClosingAutomatically: false,
                  message: messages,
                });
              }
            }
          } catch (error) {
            console.error("Submission error:", error);
          } finally {
            setLoading(false);
          }
        };

  return (
    <>
      {BackendFormData && (
        <StyledForm>
          <H3>{BackendFormData.label}</H3>
          {BackendFormData.input_fields.map((inputField) => (
            <InputField key={inputField.name} onChange={handleChange} {...inputField} />
          ))}
          <StyledSubmitDiv>
            <SubmitButton
              isDisabled={
                previousStepCalculationStatus === "incomplete" ||
                previousStepCalculationStatus === "failed"
              }
              text={isloading ? "Loading..." : buttonText}
              onClick={handleSubmit}
            />
          </StyledSubmitDiv>
        </StyledForm>
      )}
    </>
  );
});

const InputField: React.FC<BackendInputFieldProps> = memo(function InputField({
  type,
  name,
  onChange,
  options,
  isVisible,
  ...props
}) {
  const handleInputChange = (value: BackendInputValueType) => {
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
