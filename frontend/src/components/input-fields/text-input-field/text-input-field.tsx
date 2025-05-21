import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { color, fontSize, size, spacing } from "../../../theme";
import { InputContainer } from "../input-container";
import { TextInputFieldProps } from "./text-input-field.props";

const StyledInput = styled.input<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) => size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

export const TextInputField: React.FC<TextInputFieldProps> = ({
  value: initialValue = "",
  placeholder,
  onChange,
  characterLimit = -1,
  subscript,
  ...props
}) => {
  const [value, setValue] = useState(initialValue);

  useEffect(() => {
    onChange(initialValue);
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = (value: string) => {
    if (characterLimit >= 0 && value.length > characterLimit) {
      return;
    }
    setValue(value);
    onChange(value);
  };

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  const combinedSubscript =
    characterLimit >= 0
      ? `${subscript ? `${subscript} | ` : ""}Character Limit ${value.length.toString()}/${characterLimit.toString()}`
      : subscript;

  return (
    <InputContainer subscript={combinedSubscript} {...props}>
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
