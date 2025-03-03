import { useRef, useState } from "react";
import { styled } from "styled-components";

import { fontSize } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import { NumberInputFieldProps } from "./number-input-field.props";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
`;

export const NumberInputField: React.FC<NumberInputFieldProps> = ({
  defaultValue = 0,
  placeholder,
  min,
  max,
  step,
  isInteger = false,
  onChange,
  ...props
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const [, setValue] = useState<number>(() => {
    onChange(defaultValue);
    return defaultValue;
  });

  const [displayValue, setDisplayValue] = useState<string>(
    String(defaultValue),
  );

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (newValue === "" || newValue === "-" || !isNaN(Number(newValue))) {
      if (isInteger && newValue.includes(".")) {
        return;
      }

      setDisplayValue(newValue);

      const numericValue = Number(newValue);
      const newNumericValue = isNaN(numericValue) ? 0 : numericValue;
      setValue(newNumericValue);
      onChange(newNumericValue);
    }
  };

  return (
    <FrameInputField {...props}>
      <StyledInput
        ref={inputRef}
        type="text"
        inputMode="numeric"
        value={displayValue}
        placeholder={placeholder}
        min={min}
        max={max}
        step={step}
        onInput={handleInput}
        {...props}
      />
    </FrameInputField>
  );
};
