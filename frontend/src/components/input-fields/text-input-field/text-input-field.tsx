import React, { forwardRef } from "react";
import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { fontSize } from "../../../theme";
import { TextInputFieldProps } from "./text-input-field.props";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
`;

export const TextInputField = forwardRef<HTMLInputElement, TextInputFieldProps>(
  ({ value, placeholder, min, max, step, onChange, ...props }, ref) => {
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = event.target.value;
      if (onChange) {
        onChange(inputValue);
      }
    };

    return (
      <FrameInputField {...props}>
        <StyledInput
          type="text"
          value={value ?? ""}
          placeholder={placeholder}
          onChange={handleChange}
          ref={ref}
          {...props}
        />
      </FrameInputField>
    );
  },
);
