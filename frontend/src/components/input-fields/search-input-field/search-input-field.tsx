import { forwardRef, useState } from "react";
import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { fontSize } from "../../../theme";
import { SearchInputFieldProps } from "./search-input-field.props";

const StyledInput = styled.input`
  font-size: ${fontSize("default")};
`;

const SearchIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="gray"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

export const SearchInputField = forwardRef<
  HTMLInputElement,
  SearchInputFieldProps
>(({ defaultValue = "", placeholder, onChange, ...props }) => {
  const [value, setValue] = useState<string>(defaultValue);

  const handleChange = (value: string) => {
    setValue(value);
    onChange?.(value);
  };

  return (
    <FrameInputField {...props} inlinePrefix={<SearchIcon />}>
      <StyledInput
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => handleChange(e.target.value)}
        {...props}
      />
    </FrameInputField>
  );
});
