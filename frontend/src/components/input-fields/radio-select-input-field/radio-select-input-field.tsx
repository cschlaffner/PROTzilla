import { FrameInputField } from "../frame-input-field";
import { RadioSelectInputFieldProps } from "./radio-select-input-field.props";
import { spacing } from "../../../theme";
import styled from "styled-components";
import { useState } from "react";

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
  selectedValue: selectedValueProp = options[0].value,
  onChange,
  ...props
}) => {
  const [selectedValue, setSelectedValue] = useState<string>(selectedValueProp);

  const handleChange = (value: string) => {
    setSelectedValue(value);
    onChange?.(value);
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
                checked={selectedValue === option.value}
                onChange={() => handleChange(option.value)}
              />
              {option.label}
            </StyledLabel>
          );
        })}
      </StyledRadioContainer>
    </FrameInputField>
  );
};
