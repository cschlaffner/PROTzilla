import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { RadioSelectInputFieldProps } from "./radio-select-input-field.props";
import { spacing } from "../../../theme";

const StyledRadioContainer = styled.div`
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

const StyledRadio = styled.input`
  // margin-right: ${spacing("small")};
`;


export const RadioSelectInputField: React.FC<RadioSelectInputFieldProps> = ({
    options,
    selectedValue,
    onChange,
    ... props
}) => {
    return (
        <FrameInputField {...props}>
            <StyledRadioContainer>
                {options.map((option) => {
                    const id = `radio-${option.value}`; 
                    return (
                    <StyledLabel key={option.value} htmlFor={id}>
                        <StyledRadio
                            id={id}
                            type="radio"
                            value={option.value}
                            checked={selectedValue === option.value}
                            onChange={() => onChange(option.value)}
                        />
                        {option.label}
                    </StyledLabel>
                    );
                })}
            </StyledRadioContainer>
        </FrameInputField>
    );
};