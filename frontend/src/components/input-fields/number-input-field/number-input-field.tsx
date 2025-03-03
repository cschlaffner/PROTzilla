import { useEffect, useRef, useState } from "react";
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
  onChange,
  ...props
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [value, setValue] = useState<number>(defaultValue);
  const [displayValue, setDisplayValue] = useState<string>(
    String(defaultValue),
  );

  useEffect(() => {
    onChange(value);
  }, [onChange, value]);

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (newValue === "" || newValue === "-" || !isNaN(Number(newValue))) {
      setDisplayValue(newValue);

      const numericValue = Number(newValue);
      setValue(isNaN(numericValue) ? 0 : numericValue);
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
