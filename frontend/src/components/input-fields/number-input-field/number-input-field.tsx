import React, { forwardRef } from "react";
import { NumberInputFieldProps } from "./number-input-field.props";
import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { fontSize, spacing } from "../../../theme";


const StyledInput = styled.input`
  font-size: ${fontSize("default")};;
  width: 100px;
  border: none;
  outline: none;
  background-color: transparent;
`;

const InputContainer = styled.div`
  display: flex;
  align-items: center;
`;

const StyledUnit = styled.span`
  font-size: ${fontSize("default")};
  margin-left: ${spacing("verySmall")};
`;

export const NumberInputField = forwardRef<HTMLInputElement, NumberInputFieldProps>(
    ({ label, value, placeholder, min, max, step, unit, onChange, ...props }, ref) => {
      const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const inputValue = event.target.value;
        const numValue = inputValue === "" ? undefined : parseFloat(inputValue);
        if (onChange) {
          onChange(numValue ?? 0);
        }
      };
  
      return (
        <FrameInputField label={label}>
          <InputContainer>
            {unit && <StyledUnit>{unit}</StyledUnit>}
            <StyledInput
              type="number"
              value={value ?? ""}
              placeholder={placeholder}
              min={min}
              max={max}
              step={step}
              onChange={handleChange}
              ref={ref}
              {...props}
            />
          </InputContainer>
        </FrameInputField>
      );
    }
  );