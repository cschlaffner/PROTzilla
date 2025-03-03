import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { fontSize } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import { TextInputFieldProps } from "./text-input-field.props";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
  width: 100%;
`;

export const TextInputField: React.FC<TextInputFieldProps> = ({
  defaultValue = "",
  placeholder,
  onChange,
  ...props
}) => {
  const [value, setValue] = useState<string>(defaultValue);

  useEffect(() => {
    onChange(value);
  }, [onChange, value]);

  const handleChange = (value: string) => {
    setValue(value);
  };

  return (
    <FrameInputField {...props}>
      <StyledInput
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => {
          handleChange(e.target.value);
        }}
        {...props}
      />
    </FrameInputField>
  );
};
