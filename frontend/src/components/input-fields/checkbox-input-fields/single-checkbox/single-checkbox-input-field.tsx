import { useState } from "react";
import { styled } from "styled-components";

import { SingleCheckboxInputFieldProps } from "./single-checkbox-input-field.props.ts";
import { size } from "../../../../theme";
import { InputContainer } from "../../frame-input-field";
import {
  StyledCheckboxContainer,
  StyledLabel,
} from "../checkbox-select-input-field";

const StyledSingleCheckboxContainer = styled(StyledCheckboxContainer)`
  justify-content: center;
  padding-top: 0px;
  padding-bottom: 0px;
  height: ${({ $isSmall }) =>
    $isSmall ? size("inputFieldHeightSmall") : size("inputFieldHeightDefault")};
`;

export const SingleCheckboxInputField: React.FC<
  SingleCheckboxInputFieldProps
> = ({ value: initialValue, text, onChange, ...props }) => {
  const [isChecked, setIsChecked] = useState<boolean>(() => {
    onChange(initialValue ?? false);
    return initialValue ?? false;
  });

  const handleChange = (value: boolean) => {
    setIsChecked(value);
    onChange(value);
  };

  return (
    <InputContainer {...props}>
      <StyledSingleCheckboxContainer $isSmall={props.isSmall ?? false}>
        <StyledLabel htmlFor={"checkbox"}>
          <input
            type="checkbox"
            id={"checkbox"}
            checked={isChecked}
            onChange={(e) => {
              handleChange(e.target.checked);
            }}
          />
          {text}
        </StyledLabel>
      </StyledSingleCheckboxContainer>
    </InputContainer>
  );
};
