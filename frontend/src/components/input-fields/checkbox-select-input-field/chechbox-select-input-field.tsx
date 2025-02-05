import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { CheckboxSelectInputFieldProps } from "./checkbox-select-input-field.props";
import { spacing } from "../../../theme";

const StyledCheckboxContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("small")};
  cursor: default;
`;

const StyledLabel = styled.label`
    display: flex;
    align-items: center;
    gap: ${spacing("small")};
    cursor: pointer;
`;

const StyledCheckbox = styled.input`
  // margin-right: ${spacing("small")};
`;


export const CheckboxSelectInputField: React.FC<CheckboxSelectInputFieldProps> = ({
    options,
    selectedValues,
    onChange,
    ... props
}) => {
    const handleChange = (value: string) => {
        const newSelectedValues = selectedValues.includes(value)
          ? selectedValues.filter((v) => v !== value)
          : [...selectedValues, value];

        onChange(newSelectedValues);
      };

    return (
        <FrameInputField {...props}>
            <StyledCheckboxContainer>
                {options.map((option) => {
                    const id = `checkbox-${option.value}`; 
                    return (
                      <StyledLabel key={option.value} htmlFor={id}>
                        <StyledCheckbox
                          id={id}
                          type="checkbox"
                          value={option.value}
                          checked={selectedValues.includes(option.value)}
                          onChange={() => handleChange(option.value)}
                        />
                        {option.label}
                      </StyledLabel>
                    );
                })}
            </StyledCheckboxContainer>
        </FrameInputField>
    );
};