import { color, fontSize, size, spacing } from "@protzilla/theme";
import { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import { TextInputFieldProps } from "./text-input-field.props";
import { InputContainer } from "../input-container";

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

  const wasThereInputAfterHandleBlurRef = useRef(false);

  const handleChange = (value: string) => {
    if (characterLimit >= 0 && value.length > characterLimit) {
      return;
    }
    setValue(value);
    if (!wasThereInputAfterHandleBlurRef.current) {
      wasThereInputAfterHandleBlurRef.current = true;
      onChange(value);
    }
  };

  const handleBlur = () => {
    wasThereInputAfterHandleBlurRef.current = false;
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
        onBlur={handleBlur}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleBlur();
            (e.target as HTMLInputElement).blur();
          }
        }}
        $isSmall={props.isSmall ?? false}
        {...props}
      />
    </InputContainer>
  );
};
