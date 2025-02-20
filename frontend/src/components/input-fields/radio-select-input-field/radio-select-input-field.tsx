import { forwardRef, useImperativeHandle, useState } from "react";
import { styled } from "styled-components";

import { FrameInputField } from "../frame-input-field";
import {
  RadioSelectInputFieldProps,
  RadioSelectInputFieldRef,
} from "./radio-select-input-field.props";
import { spacing } from "../../../theme";

const StyledRadioContainer = styled.div`
  cursor: default;
  display: inline-flex;
  flex-direction: column;
  gap: ${spacing("small")};
`;

const StyledLabel = styled.label`
  align-items: center;
  cursor: pointer;
  display: inline-flex;
  gap: ${spacing("small")};
  max-width: fit-content;
  user-select: none;
`;

export const RadioSelectInputField = forwardRef<
  RadioSelectInputFieldRef,
  RadioSelectInputFieldProps
>(function RadioSelectInputField(
  { options, selectedValue: selectedValueProp, onChange, ...props },
  ref,
) {
  const [selectedValue, setSelectedValue] = useState<string>(
    selectedValueProp ?? options[0]?.value,
  );

  const handleChange = (value: string) => {
    setSelectedValue(value);
    onChange(value);
  };

  useImperativeHandle(ref, () => ({
    getValue: () => selectedValue,
    setValue: (newValue: string) => {
      setSelectedValue(newValue);
    },
  }));

  return (
    <FrameInputField {...props}>
      <StyledRadioContainer>
        {options.map((option) => {
          const id = `radio-${option.value}`;
          return (
            <StyledLabel key={option.value} htmlFor={id}>
              <input
                id={id}
                type="radio"
                value={option.value}
                checked={selectedValue === option.value}
                onChange={() => {
                  handleChange(option.value);
                }}
              />
              {option.label}
            </StyledLabel>
          );
        })}
      </StyledRadioContainer>
    </FrameInputField>
  );
});
