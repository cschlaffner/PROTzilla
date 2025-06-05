import { border, borderColors, color, fontSize, size, spacing } from "@protzilla/theme";
import { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import { NumberInputFieldProps } from "./number-input-field.props";
import { GrayButton } from "../../button";
import { InputContainer } from "../input-container";

const InputWithButtonsWrapper = styled.div`
  display: flex;
  align-items: center;
  width: 100%;
`;

const StyledInput = styled.input.withConfig({
  shouldForwardProp: (prop) => !["info"].includes(String(prop)),
})<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) => size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

const StepButtonContainer = styled.div<{ $isLastElement: boolean }>`
  height: ${size("inputFieldHeightDefault")};
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  background-color: ${color("gray6")};
  border-radius: ${({ $isLastElement }) => ($isLastElement ? `0 6px 6px 0` : `0`)};
  border-left: ${border("defaultStrength")} solid ${borderColors("default")};
  overflow: hidden;
`;

const StepButton = styled(GrayButton)`
  border-radius: 0px;
  background-color: ${color("gray6")};
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
  separateSuffix,
  ...props
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const [displayValue, setDisplayValue] = useState<string>(String(value));

  function formatNumber(num: number, digits = 10): string {
    const rounded = Number(num.toFixed(digits));
    return isNaN(rounded) ? "" : rounded.toString();
  }

  useEffect(() => {
    setDisplayValue(formatNumber(value));
  }, [value]);

  const hasMin = typeof min === "number";
  const hasMax = typeof max === "number";

  const handleChange = (e: { target: { value: string } }) => {
    const raw = e.target.value;

    if (!/^[-\d.]*$/.test(raw)) return;
    if (isInteger && raw.includes(".")) return;

    setDisplayValue(raw);
  };

  const handleBlur = () => {
    if (displayValue === "" || displayValue === "-") {
      setDisplayValue(String(Math.max(0, min ?? 0)));
      return;
    }

    const num = isInteger ? parseInt(displayValue, 10) : parseFloat(displayValue);

    if (isNaN(num)) {
      setDisplayValue(String(value));
      return;
    }

    if (hasMin && num < min) {
      setDisplayValue(String(min));
      onChange(min);
      return;
    }
    if (hasMax && num > max) {
      setDisplayValue(String(max));
      onChange(max);
      return;
    }

    const cleaned = isInteger ? String(Math.floor(num)) : String(num);
    setDisplayValue(cleaned);
    onChange(num);
  };

  useEffect(() => {
    setDisplayValue(String(value));
  }, [value]);

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

    const formattedValue = Number(formatNumber(newValue, 10));
    setDisplayValue(String(formattedValue));
    onChange(formattedValue);
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
          onChange={handleChange}
          onBlur={handleBlur}
          // Disable isSmall when hasStepButtons is true
          $isSmall={hasStepButtons ? false : (props.isSmall ?? false)}
          {...props}
        />
        {hasStepButtons && (
          <StepButtonContainer $isLastElement={!separateSuffix}>
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
        )}
      </InputWithButtonsWrapper>
    </InputContainer>
  );
};
