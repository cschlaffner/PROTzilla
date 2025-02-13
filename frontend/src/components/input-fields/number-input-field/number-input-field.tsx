import { fontSize } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import { NumberInputFieldProps } from "./number-input-field.props";
import { forwardRef, useState } from "react";
import styled from "styled-components";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
`;

export const NumberInputField = forwardRef<
  HTMLInputElement,
  NumberInputFieldProps
>(({ defaultValue = 0, placeholder, min, max, step, onChange, ...props }, ref) => {
  const [value, setValue] = useState<string>(String(defaultValue));

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value;

    if (newValue === "-" || newValue === "") {
      setValue(newValue);
      return;
    }

    const numericValue = Number(newValue);
    if (!isNaN(numericValue)) {
      setValue(newValue);
      onChange?.(numericValue);
    }
  };

  return (
    <FrameInputField {...props}>
      <StyledInput
        ref={ref}
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
