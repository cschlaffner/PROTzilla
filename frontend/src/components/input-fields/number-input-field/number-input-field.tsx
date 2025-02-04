import React, { forwardRef } from "react";
import { NumberInputFieldProps } from "./number-input-field.props";
import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { fontSize, spacing } from "../../../theme";

const StyledInputContainer = styled.div`
  display: flex;
  gap: ${spacing("verySmall")};
`;

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
  border: none;
  outline: none;
  background-color: transparent;
  padding: ${spacing("small")};
`;

const StyledUnit = styled.div`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("verySmall")};
  border-right: 2px solid #ccc;
  border-radius: calc(${spacing("small")} - 2px) 0px 0px calc(${spacing("small")} - 2px);
  background: #eee;
  display: flex;
  align-items: center;
  box-sizing: content-box;
`;

export const NumberInputField = forwardRef<HTMLInputElement, NumberInputFieldProps>(
    ({ value, placeholder, min, max, step, unit, onChange, ...props }, ref) => {
      const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const inputValue = event.target.value;
        const numValue = inputValue === "" ? undefined : parseFloat(inputValue);
        if (onChange) {
          onChange(numValue ?? 0);
        }
      };
  
      return (
        <FrameInputField {...props}>
          <StyledInputContainer>
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
          </StyledInputContainer>
        </FrameInputField>
      );
    }
  );