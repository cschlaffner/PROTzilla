import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { FrameInputField } from "../frame-input-field";
import { RadioSelectInputFieldProps } from "./radio-select-input-field.props";
import { spacing } from "../../../theme";

const StyledRadioContainer = styled.div`
  cursor: default;
  display: inline-flex;
  flex-direction: column;
  gap: ${spacing("small")};
`;

const StyledLabel = styled.label`
  align-items: center;
  cursor: pointer;
  display: inline-flex;
  gap: ${spacing("small")};
  max-width: fit-content;
  user-select: none;
`;

export const RadioSelectInputField: React.FC<RadioSelectInputFieldProps> = ({
  options,
  defaultOption,
  onChange,
  ...props
}) => {
  const [value, setValue] = useState<string>(
    defaultOption ?? options[0]?.value,
  );

  useEffect(() => {
    onChange(value);
  }, [onChange, value]);

  const handleChange = (value: string) => {
    setValue(value);
  };

  return (
    <FrameInputField {...props}>
      <StyledRadioContainer>
        {options.map((option) => {
          const id = `radio-${option.value}`;
          return (
            <StyledLabel key={option.value} htmlFor={id}>
              <input
                id={id}
                type="radio"
                value={option.value}
                checked={value === option.value}
                onChange={() => {
                  handleChange(option.value);
                }}
              />
              {option.label}
            </StyledLabel>
          );
        })}
      </StyledRadioContainer>
    </FrameInputField>
  );
};
