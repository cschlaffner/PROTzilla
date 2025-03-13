import { useState } from "react";

import { color, fontSize, size, spacing, styled } from "../../../theme";
import { InputContainer } from "../input-container";
import { SearchInputFieldProps } from "./search-input-field.props";
import { Icon } from "../../icon";

const StyledInput = styled.input<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) =>
    size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

export const SearchInputField: React.FC<SearchInputFieldProps> = ({
  value: initialValue = "",
  placeholder,
  onChange,
  ...props
}) => {
  const [value, setValue] = useState(() => {
    onChange(initialValue);
    return initialValue;
  });

  const handleChange = (value: string) => {
    setValue(value);
    onChange(value);
  };

  return (
    <InputContainer
      {...props}
      inlinePrefix={
        <Icon icon="searchLens" {...(props.isSmall ? { isSmall: true } : {})} />
      }
    >
      <StyledInput
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => {
          handleChange(e.target.value);
        }}
        $isSmall={props.isSmall ?? false}
        {...props}
      />
    </InputContainer>
  );
};
