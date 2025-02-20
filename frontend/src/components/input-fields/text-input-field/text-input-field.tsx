import { forwardRef, useImperativeHandle, useState } from "react";
import { styled } from "styled-components";

import { fontSize } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import {
  TextInputFieldProps,
  TextInputFieldRef,
} from "./text-input-field.props";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
  width: 100%;
`;

export const TextInputField = forwardRef<
  TextInputFieldRef,
  TextInputFieldProps
>(function TextInputField(
  { defaultValue = "", placeholder, onChange, ...props },
  ref,
) {
  const [value, setValue] = useState<string>(defaultValue);

  const handleChange = (value: string) => {
    setValue(value);
    onChange(value);
  };

  useImperativeHandle(ref, () => ({
    getValue: () => value,
    setValue: (newValue: string) => {
      setValue(newValue);
    },
  }));

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
});
