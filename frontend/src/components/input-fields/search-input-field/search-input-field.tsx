import { useState } from "react";
import { styled } from "styled-components";

import { color, fontSize, size, spacing } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
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
  defaultValue = "",
  placeholder,
  onChange,
  ...props
}) => {
  const [value, setValue] = useState(() => {
    onChange(defaultValue);
    return defaultValue;
  });

  const handleChange = (value: string) => {
    setValue(value);
    onChange(value);
  };

  return (
    <FrameInputField
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
    </FrameInputField>
  );
};
