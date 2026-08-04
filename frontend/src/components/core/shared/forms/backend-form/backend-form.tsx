import { useNotification } from "@protzilla/app";
import { border, borderColors, color, fontSize, spacing, useTheme } from "@protzilla/theme";
import { CalculationMessage, callApiWithParameters } from "@protzilla/utils";
import React, { memo, useCallback, useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import {
  BackendFormData,
  BackendFormProps,
  BackendInputFieldProps,
  BackendInputValueType,
  NamedHandle,
} from "./backend-form.props";
import { Button } from "../../button";
import {
  CheckboxSelectInputField,
  ColorInputField,
  DropdownInputField,
  FileInputField,
  FormDivider,
  HeaderInfoField,
  InfoField,
  MultiSelectInputField,
  NumberInputField,
  RadioSelectInputField,
  SearchInputField,
  SingleCheckboxInputField,
  TextInputField,
} from "../../input-fields";
import { NameModal } from "../../modal";
import { H3 } from "../../text";

const StyledForm = styled.div`
  width: auto;
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

const HandleList = styled.div`
  display: grid;
  gap: ${spacing("verySmall")};
  padding: ${spacing("verySmall")} 0 ${spacing("small")};
`;

const HandleRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: ${spacing("verySmall")};
`;

const HandleControl = styled.input`
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  min-width: 0;
  padding: ${spacing("verySmall")};
`;

const HandleSelect = styled(HandleControl).attrs({ as: "select" })``;

export const BackendForm: React.FC<BackendFormProps> = memo(function Form({
  runName,
  buttonText,
  previousStepCalculationStatus,
  currentStepCalculationStatus,
  current_step_id,
  isLastStep,
  onNext,
  onSubmit,
  onChange,
  runData,
}) {
  const notify = useNotification();
  const theme = useTheme();

  const [BackendFormData, setBackendFormData] = useState<BackendFormData>();
  const [isloading, setLoading] = useState(false);
  const [isCustomStepNameOpen, setIsCustomStepNameOpen] = useState(false);
  const formUpdateRef = useRef(Promise.resolve());

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
  }, [current_step_id, getStepForm, runData]);

  const handleChange = (name: string, value: BackendInputValueType) => {
    formUpdateRef.current = formUpdateRef.current
      .then(() => getStepForm({ [name]: value }))
      .then(onChange);
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

  const saveCustomStep = async (name: string) => {
    const response = await callApiWithParameters("custom_steps/", {
      action: "save",
      run_name: runName,
      step_id: current_step_id,
      name,
    });
    notify({
      type: response.success ? "success" : "error",
      title: response.success ? "Custom step saved" : "Could not save custom step",
      message: response.message,
    });
    if (response.success) setIsCustomStepNameOpen(false);
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
            {runData.current_section === "custom" && (
              <Button
                text="Save Custom Step"
                onPress={() => {
                  setIsCustomStepNameOpen(true);
                }}
              />
            )}
            <SubmitButton
              isDisabled={
                previousStepCalculationStatus === "incomplete" ||
                previousStepCalculationStatus === "failed" ||
                (isLastStep && currentStepCalculationStatus === "complete")
              }
              text={isloading ? "Loading..." : buttonText}
              onPress={handleSubmit}
            />
          </StyledSubmitDiv>
        </StyledForm>
      )}
      <NameModal
        title="Save custom step"
        label="With custom step name:"
        submitLabel="Save custom step"
        isOpen={isCustomStepNameOpen}
        onClose={() => {
          setIsCustomStepNameOpen(false);
        }}
        onSubmit={(name) => {
          void saveCustomStep(name);
        }}
      />
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
    case "color":
      return <ColorInputField onChange={handleInputChange} {...props} />;
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
    case "named-handles":
      return (
        <NamedHandlesInputField
          label={props.label}
          value={props.value as NamedHandle[]}
          options={options ?? []}
          onChange={handleInputChange}
        />
      );
    case "file":
      return <FileInputField onChange={handleInputChange} {...props} />;
    case "form-divider":
      return <FormDivider {...props} />;
    case "info-field":
      return <InfoField {...props} />;
    case "header-info-field":
      return <HeaderInfoField {...props} />;
    default:
      return null;
  }
});

const NamedHandlesInputField: React.FC<{
  label?: string;
  value: NamedHandle[];
  options: { label: string; value: string }[];
  onChange: (value: NamedHandle[]) => void;
}> = ({ label, value, options, onChange }) => {
  const [handles, setHandles] = useState(value);

  useEffect(() => {
    setHandles(value);
  }, [value]);

  const commit = (next: NamedHandle[]) => {
    setHandles(next);
    onChange(next);
  };

  const uniqueName = (name: string, index = -1) => {
    const base =
      name
        .trim()
        .replace(/\W/g, "_")
        .replace(/^(?=\d)/, "_") || "value";
    let candidate = base;
    let suffix = 2;
    while (
      handles.some((handle, handleIndex) => handleIndex !== index && handle.name === candidate)
    ) {
      candidate = `${base}_${String(suffix++)}`;
    }
    return candidate;
  };

  const addHandle = () => {
    const type = options.find((option) => option.value === "custom_df")?.value ?? options[0]?.value;
    if (type) {
      commit([...handles, { name: uniqueName(type), type }]);
    }
  };

  return (
    <HandleList>
      <strong>{label}</strong>
      {handles.map((handle, index) => (
        <HandleRow key={index}>
          <HandleSelect
            aria-label="Data type"
            value={handle.type}
            onChange={(event) => {
              commit(
                handles.map((item, itemIndex) =>
                  itemIndex === index ? { ...item, type: event.target.value } : item,
                ),
              );
            }}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </HandleSelect>
          <HandleControl
            aria-label="Variable name"
            placeholder="Variable name"
            value={handle.name}
            onChange={(event) => {
              setHandles(
                handles.map((item, itemIndex) =>
                  itemIndex === index ? { ...item, name: event.target.value } : item,
                ),
              );
            }}
            onBlur={() => {
              commit(
                handles.map((item, itemIndex) =>
                  itemIndex === index ? { ...item, name: uniqueName(item.name, index) } : item,
                ),
              );
            }}
          />
          <Button
            icon="trash"
            isSmall
            aria-label="Remove handle"
            onPress={() => {
              commit(handles.filter((_, itemIndex) => itemIndex !== index));
            }}
          />
        </HandleRow>
      ))}
      <Button
        icon="add"
        isSmall
        text={`Add ${label?.toLowerCase().replace(/s$/, "") ?? "handle"}`}
        onPress={addHandle}
      />
    </HandleList>
  );
};
