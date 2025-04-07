import { useState } from "react";

import { InputContainer } from "../frame-input-field";
import { SingleCheckboxInputFieldProps } from "./single-checkbox-input-field.props.ts";
import {
  StyledCheckboxContainer,
  StyledLabel,
} from "../checkbox-select-input-field";

export const SingleCheckboxInputField: React.FC<
  SingleCheckboxInputFieldProps
> = ({ value: initialValue, text, onChange, isShy, ...props }) => {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  const [value, setValue] = useState<boolean>(() => {
    onChange(initialValue);
    return initialValue;
  });

  const handleChange = (value: boolean) => {
    setValue(value);
    onChange(value);
  };

  return (
    <InputContainer smallBorder={isShy} {...props}>
      <StyledCheckboxContainer $isSmall={props.isSmall ?? false}>
        <StyledLabel htmlFor={"checkbox"}>
          <input
            type="checkbox"
            id={"checkbox"}
            checked={value}
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
