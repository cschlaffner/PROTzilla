import { useState } from "react";

import { SingleCheckboxInputFieldProps } from "./single-checkbox-input-field.props.ts";
import { InputContainer } from "../../frame-input-field";
import {
  StyledCheckboxContainer,
  StyledLabel,
} from "../checkbox-select-input-field";

export const SingleCheckboxInputField: React.FC<
  SingleCheckboxInputFieldProps
> = ({ value: initialValue, text, onChange, ...props }) => {
  const [isChecked, setisChecked] = useState<boolean>(() => {
    onChange(initialValue);
    return initialValue;
  });

  const handleChange = (value: boolean) => {
    setisChecked(value);
    onChange(value);
  };

  return (
    <InputContainer {...props}>
      <StyledCheckboxContainer $isSmall={props.isSmall ?? false}>
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
      </StyledCheckboxContainer>
    </InputContainer>
  );
};
