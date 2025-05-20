import { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import { border, borderColors, color, fontSize, size, spacing } from "../../../theme";
import { InputContainer } from "../input-container";
import { NumberInputFieldProps } from "./number-input-field.props";
import { GrayButton } from "../../button";

const InputWithButtonsWrapper = styled.div`
  display: flex;
  align-items: center;
  width: 100%;
`;

const StyledInput = styled.input<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) => size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: calc(100% - 10px);
`;

const StepButtonContainer = styled.div<{ $isLastElement: boolean }>`
  height: ${size("inputFieldHeightDefault")};
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0;
  background-color: #e4e4e5;

  border-radius: ${({ $isLastElement }) => ($isLastElement ? `0 6px 6px 0` : `0`)};

  border-left: ${border("defaultStrength")} solid ${borderColors("default")};

  overflow: hidden;
`;

const StepButtonContainerWithMargin = styled(StepButtonContainer)`
  margin-right: -${spacing("verySmall")};
`;

const StepButton = styled(GrayButton)`
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
  subscript,
  onChange,
  ...props
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const [displayValue, setDisplayValue] = useState<string>(String(value));

  useEffect(() => {
    setDisplayValue(Number(value.toFixed(10)).toString());
  }, [value]);

  const hasMin = typeof min === "number";
  const hasMax = typeof max === "number";

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value;
    if (newValue === "" || newValue === "-" || !isNaN(Number(newValue))) {
      if (isInteger && newValue.includes(".")) {
        return;
      }

      if (hasMax && Number(newValue) > max) {
        newValue = max.toString();
      }
      if (hasMin && Number(newValue) < min) {
        newValue = min.toString();
      }

      setDisplayValue(newValue);

      const numericValue = Number(newValue);
      const newNumericValue = isNaN(numericValue) ? 0 : numericValue;
      onChange(newNumericValue);
    }
  };

  const handleClick = (direction: "up" | "down") => {
    const stepValue = step ?? 1;
    let newValue = value;

    if (direction === "up") {
      newValue = value + stepValue;
      if (hasMax) {
        newValue = Math.min(newValue, max);
      }
    } else {
      newValue = value - stepValue;
      if (hasMin) {
        newValue = Math.max(newValue, min);
      }
    }
    setDisplayValue(Number(newValue.toFixed(10)).toString());
    onChange(newValue);
  };

  const combinedSubscript = [
    subscript,
    isInteger ? "Enter an integer" : "Enter a float",
    hasMin ? `Min: ${min.toString()}` : null,
    hasMax ? `Max: ${max.toString()}` : null,
  ]
    .filter(Boolean)
    .join(" | ");

  return (
    <InputContainer subscript={combinedSubscript} {...props}>
      <InputWithButtonsWrapper>
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
        {hasStepButtons &&
          (props.separateSuffix ? (
            <StepButtonContainerWithMargin $isLastElement={!props.separateSuffix}>
              <StepButton
                onClick={() => {
                  handleClick("up");
                }}
                icon="triangleUp"
                color="text"
                isSmall
              />
              <StepButton
                onClick={() => {
                  handleClick("down");
                }}
                icon="triangleDown"
                color="text"
                isSmall
              />
            </StepButtonContainerWithMargin>
          ) : (
            <StepButtonContainer $isLastElement={!props.separateSuffix}>
              <StepButton
                onClick={() => {
                  handleClick("up");
                }}
                icon="triangleUp"
                color="text"
                isSmall
              />
              <StepButton
                onClick={() => {
                  handleClick("down");
                }}
                icon="triangleDown"
                color="text"
                isSmall
              />
            </StepButtonContainer>
          ))}
      </InputWithButtonsWrapper>
    </InputContainer>
  );
};
