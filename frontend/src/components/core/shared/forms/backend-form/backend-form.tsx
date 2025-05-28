import { useNotification } from "@protzilla/app";
import { color, fontSize, size, spacing, useTheme } from "@protzilla/theme";
import { CalculationMessage, callApiWithParameters } from "@protzilla/utils";
import React, { memo, useCallback, useEffect, useState } from "react";
import { styled } from "styled-components";

import {
  BackendFormData,
  BackendFormProps,
  BackendInputFieldProps,
  BackendInputValueType,
} from "./backend-form.props";
import { Button } from "../../button";
import {
  CheckboxSelectInputField,
  DropdownInputField,
  FileInputField,
  MultiSelectInputField,
  NumberInputField,
  RadioSelectInputField,
  SearchInputField,
  SingleCheckboxInputField,
  TextInputField,
} from "../../input-fields";
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
  buttonText,
  previousStepCalculationStatus,
  currentStepCalculationStatus,
  current_step_index,
  onNext,
  onSubmit,
  onChange,
}) {
  const notify = useNotification();
  const theme = useTheme();

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

  const handleNotify = (message: CalculationMessage) => {
    if (message.level >= 40) {
      notify({
        title: "Error when calculating step",
        type: "error",
        isClosingAutomatically: true,
        message: message.msg,
        traceback: message.trace,
        closeAfterMs: theme.durations.veryLongNotificationDuration,
      });
    } else if (message.level <= 20) {
      notify({
        title: "Success",
        type: "success",
        isClosingAutomatically: true,
        message: message.msg,
        closeAfterMs: theme.durations.standardNotificationDuration,
      });
    } else {
      notify({
        title: "A warning occurred",
        type: "warning",
        isClosingAutomatically: true,
        message: message.msg,
        traceback: message.trace,
        closeAfterMs: theme.durations.veryLongNotificationDuration,
      });
    }
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
            }
            const messages = response.message;
            if (Array.isArray(messages)) {
              messages.forEach((message: CalculationMessage) => {
                handleNotify(message);
              });
            } else {
              handleNotify(messages);
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
