import { useState } from "react";
import { styled } from "styled-components";

import { color, fontSize, size, spacing } from "../../../theme";
import { InputContainer } from "../frame-input-field";
import { TextInputFieldProps } from "./text-input-field.props";

const StyledInput = styled.input<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) =>
    size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

export const TextInputField: React.FC<TextInputFieldProps> = ({
  value: initialValue = "",
  placeholder,
  onChange,
  ...props
}) => {
  const [value, setValue] = useState(() => {
    onChange(initialValue);
    return initialValue;
  });

  const handleChange = (value: string) => {
    setValue(value);
    onChange(value);
  };

  return (
    <InputContainer {...props}>
      <StyledInput
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => {
          handleChange(e.target.value);
        }}
        $isSmall={props.isSmall ?? false}
        {...props}
      />
    </InputContainer>
  );
};
