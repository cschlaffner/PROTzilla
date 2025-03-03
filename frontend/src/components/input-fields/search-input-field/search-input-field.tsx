import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { fontSize } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import { SearchInputFieldProps } from "./search-input-field.props";
import { Icon } from "../../icon";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
`;

export const SearchInputField: React.FC<SearchInputFieldProps> = ({
  defaultValue = "",
  placeholder,
  onChange,
  ...props
}) => {
  const [value, setValue] = useState<string>(defaultValue);

  useEffect(() => {
    onChange(value);
  }, [onChange, value]);

  const handleChange = (value: string) => {
    setValue(value);
  };

  return (
    <FrameInputField
      {...props}
      inlinePrefix={
        <Icon
          icon="searchLens"
          {...(props.smallFrame ? { isSmall: true } : {})}
        />
      }
    >
      <StyledInput
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => {
          handleChange(e.target.value);
        }}
        {...props}
      />
    </FrameInputField>
  );
};
