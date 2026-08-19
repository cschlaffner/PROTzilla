import { size } from "@protzilla/theme";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { SingleCheckboxInputFieldProps } from "./single-checkbox-input-field.props.ts";
import { InputContainer } from "../../input-container";
import { StyledCheckboxContainer, StyledLabel } from "../checkbox-select-input-field";

const StyledSingleCheckboxContainer = styled(StyledCheckboxContainer)`
  justify-content: center;
  padding-top: 0px;
  padding-bottom: 0px;
  height: ${({ $isSmall }) =>
    $isSmall ? size("inputFieldHeightSmall") : size("inputFieldHeightDefault")};
`;

export const SingleCheckboxInputField: React.FC<SingleCheckboxInputFieldProps> = ({
  value: initialValue,
  text,
  onChange,
  id,
  ...props
}) => {
  const [isChecked, setIsChecked] = useState<boolean>(() => {
    return initialValue ?? false;
  });

  const checkboxId = id ?? "checkbox";

  useEffect(() => {
    setIsChecked(initialValue ?? false);
  }, [initialValue]);

  const handleChange = (value: boolean) => {
    setIsChecked(value);
    onChange(value);
  };

  return (
    <InputContainer {...props}>
      <StyledSingleCheckboxContainer $isSmall={props.isSmall ?? false}>
        <StyledLabel htmlFor={checkboxId}>
          <input
            type="checkbox"
            id={checkboxId}
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
