import React, { forwardRef } from "react";
import { NumberInputFieldProps } from "./number-input-field.props";
import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { fontSize } from "../../../theme";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
`;

export const NumberInputField = forwardRef<
  HTMLInputElement,
  NumberInputFieldProps
>(({ value, placeholder, min, max, step, onChange, ...props }, ref) => {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value;
    const numValue = inputValue === "" ? undefined : parseFloat(inputValue);
    if (onChange) {
      onChange(numValue ?? 0);
    }
  };

  return (
    <FrameInputField {...props}>
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
    </FrameInputField>
  );
});
