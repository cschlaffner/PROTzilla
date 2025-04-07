import { useState } from "react";
import { styled } from "styled-components";

import { CheckboxSelectInputFieldProps } from "./checkbox-select-input-field.props";
import { spacing } from "../../../theme";
import { InputContainer } from "../frame-input-field";

export const StyledCheckboxContainer = styled.div<{ $isSmall: boolean }>`
  cursor: default;
  display: inline-flex;
  flex-direction: column;
  gap: ${spacing("small")};
  padding-top: ${({ $isSmall }) =>
    $isSmall ? spacing("verySmall") : spacing("small")};
  padding-bottom: ${({ $isSmall }) =>
    $isSmall ? spacing("verySmall") : spacing("small")};
  padding-left: ${spacing("small")};
  padding-right: ${spacing("small")};
  width: 100%;
`;

export const StyledLabel = styled.label`
  align-items: center;
  cursor: pointer;
  display: inline-flex;
  gap: ${spacing("small")};
  max-width: fit-content;
  user-select: none;
`;

export const CheckboxSelectInputField: React.FC<
  CheckboxSelectInputFieldProps
> = ({ options, value = [], onChange, ...props }) => {
  const [selectedValues, setSelectedValues] = useState(() => {
    const sortedDefaultOptions = [...value].sort((a, b) => a.localeCompare(b));
    onChange(sortedDefaultOptions);
    return sortedDefaultOptions;
  });

  const handleChange = (value: string) => {
    const newSelectedValues = selectedValues.includes(value)
      ? selectedValues.filter((v) => v !== value)
      : [...selectedValues, value];

    const sortedSelection = newSelectedValues.sort((a, b) =>
      a.localeCompare(b),
    );

    setSelectedValues(sortedSelection);
    onChange(sortedSelection);
  };

  return (
    <InputContainer {...props}>
      <StyledCheckboxContainer $isSmall={props.isSmall ?? false}>
        {options.map((option) => {
          const id = `checkbox-${option.value}`;
          return (
            <StyledLabel key={option.value} htmlFor={id}>
              <input
                id={id}
                type="checkbox"
                value={option.value}
                checked={selectedValues.includes(option.value)}
                onChange={() => {
                  handleChange(option.value);
                }}
              />
              {option.label}
            </StyledLabel>
          );
        })}
      </StyledCheckboxContainer>
    </InputContainer>
  );
};
