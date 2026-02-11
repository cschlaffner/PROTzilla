import { color, size, spacing } from "@protzilla/theme";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { ColorInputFieldProps } from "./color-input-field.props";
import { InputContainer } from "../input-container";

const StyledColorInput = styled.input<{ $isSmall: boolean }>`
  appearance: none;
  background: ${color("transparent")};
  border: none;
  outline: none;
  cursor: pointer;
  
  height: ${({ $isSmall }) => size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
  padding: ${spacing("tiny")} ${spacing("small")};

  /* Removes default padding/border from the color swatch in Chrome/Safari */
  &::-webkit-color-swatch-wrapper {
    padding: 0;
  }
  &::-webkit-color-swatch {
    border: 1px solid ${color("border")};
    border-radius: 4px;
  }

  /* For Firefox */
  &::-moz-color-swatch {
    border: 1px solid ${color("border")};
    border-radius: 4px;
  }
`;

export const ColorInputField: React.FC<ColorInputFieldProps> = ({
  value: initialValue = "#000000",
  onChange,
  subscript,
  ...props
}) => {
  const [value, setValue] = useState(initialValue);

  // Sync internal state if initialValue prop changes
  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  useEffect(() => {
    onChange(initialValue);
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = (newValue: string) => {
    setValue(newValue);
    onChange(newValue);
  };

  return (
    <InputContainer subscript={subscript} {...props}>
      <StyledColorInput
        type="color"
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        $isSmall={props.isSmall ?? false}
        {...props}
      />
    </InputContainer>
  );
};
