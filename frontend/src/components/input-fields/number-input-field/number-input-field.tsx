import { forwardRef, useImperativeHandle, useRef, useState } from "react";
import { styled } from "styled-components";

import { fontSize } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import {
  NumberInputFieldProps,
  NumberInputFieldRef,
} from "./number-input-field.props";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
`;

export const NumberInputField = forwardRef<
  NumberInputFieldRef,
  NumberInputFieldProps
>(function NumberInputField(
  { defaultValue = 0, placeholder, min, max, step, onChange, ...props },
  ref,
) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [value, setValue] = useState<string>(String(defaultValue));

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;

    if (newValue === "-" || newValue === "") {
      setValue(newValue);
      return;
    }

    const numericValue = Number(newValue);
    if (!isNaN(numericValue)) {
      setValue(newValue);
      onChange(numericValue);
    }
  };

  useImperativeHandle(ref, () => ({
    getValue: () => (value === "" || value === "-" ? null : Number(value)),
    setValue: (newValue: number) => {
      setValue(String(newValue));
    },
  }));

  return (
    <FrameInputField {...props}>
      <StyledInput
        ref={inputRef}
        type="number"
        inputMode="numeric"
        value={value}
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
        onInput={handleInput}
        {...props}
      />
    </FrameInputField>
  );
});
