import { useState } from "react";
import { styled } from "styled-components";

import { color, fontSize, size, spacing } from "@protzilla/theme";
import { InputContainer } from "../input-container";
import { SearchInputFieldProps } from "./search-input-field.props";
import { Icon } from "../../icon";

const StyledInput = styled.input.withConfig({
  shouldForwardProp: (prop: string) => prop !== "isSmall" && prop !== "smallBorder",
})<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) => size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

export const SearchInputField: React.FC<SearchInputFieldProps> = ({
  value: initialValue = "",
  placeholder,
  onChange,
  style,
  isSmall,
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
    <div style={style}>
      <InputContainer
        {...props}
        isSmall={isSmall}
        inlinePrefix={<Icon icon="searchLens" {...(isSmall ? { isSmall: true } : {})} />}
      >
        <StyledInput
          type="text"
          value={value}
          placeholder={placeholder}
          onChange={(e) => {
            handleChange(e.target.value);
          }}
          $isSmall={isSmall ?? false}
        />
      </InputContainer>
    </div>
  );
};
