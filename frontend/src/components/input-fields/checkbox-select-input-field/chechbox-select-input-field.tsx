import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { CheckboxSelectInputFieldProps } from "./checkbox-select-input-field.props";
import { spacing } from "../../../theme";
import { FrameInputField } from "../frame-input-field";

const StyledCheckboxContainer = styled.div`
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

export const CheckboxSelectInputField: React.FC<
  CheckboxSelectInputFieldProps
> = ({ options, defaultOptions = [], onChange, ...props }) => {
  const [selectedValues, setSelectedValues] = useState<string[]>([]);

  useEffect(() => {
    const sortedDefaultOptions = defaultOptions.sort((a, b) =>
      a.localeCompare(b),
    );
    setSelectedValues(sortedDefaultOptions);
    onChange(sortedDefaultOptions);
  }, [defaultOptions, onChange]);

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
    <FrameInputField {...props}>
      <StyledCheckboxContainer>
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
    </FrameInputField>
  );
};
