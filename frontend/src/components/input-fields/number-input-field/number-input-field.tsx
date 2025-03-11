import { useRef, useState } from "react";
import { styled } from "styled-components";

import { color, fontSize, size, spacing } from "../../../theme";
import { InputContainer } from "../input-container";
import { NumberInputFieldProps } from "./number-input-field.props";

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

export const NumberInputField: React.FC<NumberInputFieldProps> = ({
  value = 0,
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
    onChange(value);
    return value;
  });

  const [displayValue, setDisplayValue] = useState<string>(String(value));

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
    <InputContainer {...props}>
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
        $isSmall={props.isSmall ?? false}
        {...props}
      />
    </InputContainer>
  );
};
