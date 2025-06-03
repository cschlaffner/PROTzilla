import { color, fontSize, radius, size, spacing } from "@protzilla/theme";
import { useEffect, useRef, useState } from "react";
import { css, styled } from "styled-components";

import { NumberInputFieldProps } from "./number-input-field.props";
import { GrayButton } from "../../button";
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

const StepButton = styled(GrayButton)`
  background-color: #e4e4e5;
  min-height: 0px;
  width: 15px;
  padding: 0px;
`;

const StepButtonContainer = styled.div<{ $isVisuallyLast: boolean }>`
  height: ${size("inputFieldHeightDefault")};
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0;
  ${({ $isVisuallyLast }) =>
    $isVisuallyLast
      ? css`
          ${StepButton}:first-child {
            border-radius: 0 ${radius("button")} 0 0;
          }
          ${StepButton}:last-child {
            border-radius: 0 0 ${radius("button")} 0;
          }
        `
      : css`
          margin-right: -${spacing("verySmall")};
          ${StepButton} {
            border-radius: 0;
          }
        `}
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
      onChange(newNumericValue);
    }
  };

  const handleClick = (
    e: React.PointerEvent<HTMLButtonElement> | React.KeyboardEvent<HTMLButtonElement>,
  ) => {
    const { id } = e.currentTarget;
    const stepValue = step ?? 1;
    let newValue = value;
    if (id.includes("up")) {
      newValue = value + stepValue;
      if (max !== undefined) {
        newValue = Math.min(newValue, max);
      }
    } else if (id.includes("down")) {
      newValue = value - stepValue;
      if (min !== undefined) {
        newValue = Math.max(newValue, min);
      }
    }
    onChange(newValue);
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
        // Disable isSmall when hasStepButtons is true
        $isSmall={hasStepButtons ? false : (props.isSmall ?? false)}
        {...props}
      />
      {hasStepButtons && (
        <StepButtonContainer $isVisuallyLast={!props.separateSuffix}>
          <StepButton id="up" onPress={handleClick} icon="triangleUp" color="text" isSmall={true} />
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
