import { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import {
  border,
  borderColors,
  color,
  fontSize,
  size,
  spacing,
} from "../../../theme";
import { InputContainer } from "../frame-input-field";
import { NumberInputFieldProps } from "./number-input-field.props";
import { GrayButton } from "../../button";

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

const StepButtonContainer = styled.div`
  height: 30px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0;
  margin-right: -${spacing("verySmall")};
`;

const StepButton = styled(GrayButton)`
  border-left: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: 0px;
  background-color: #e4e4e5;
  min-height: 0px;
  width: 15px;
  padding: 0px;
`;

export const NumberInputField: React.FC<NumberInputFieldProps> = ({
  value = 0,
  placeholder,
  min,
  max,
  step,
  hasStepButtons = false,
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

  useEffect(() => {
    setDisplayValue(String(value));
  }, [value]);

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

  const handleClick = (
    e:
      | React.PointerEvent<HTMLButtonElement>
      | React.KeyboardEvent<HTMLButtonElement>,
  ) => {
    const { id } = e.currentTarget;
    setValue((prevValue) => {
      const stepValue = step ?? 1;
      let updatedValue = prevValue;
      if (id === "up") {
        updatedValue = prevValue + stepValue;
        if (max !== undefined && updatedValue > max) {
          updatedValue = max;
        }
      } else if (id === "down") {
        updatedValue = prevValue - stepValue;
        if (min !== undefined && updatedValue < min) {
          updatedValue = min;
        }
      }
      setDisplayValue(String(updatedValue));
      onChange(updatedValue);
      return updatedValue;
    });
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
      {hasStepButtons && (
        <StepButtonContainer>
          <StepButton
            id="up"
            onPress={handleClick}
            icon="triangleUp"
            color="text"
            isSmall={true}
          />
          <StepButton
            id="down"
            onPress={handleClick}
            icon="triangleDown"
            color="text"
            isSmall={true}
          />
        </StepButtonContainer>
      )}
    </InputContainer>
  );
};
