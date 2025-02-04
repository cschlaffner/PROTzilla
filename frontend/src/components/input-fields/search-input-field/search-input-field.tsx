import React, { forwardRef, useRef } from "react";
import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { fontSize, spacing } from "../../../theme";
import { SearchInputFieldProps } from "./search-input-field.props";

const StyledInputContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing("verySmall")};
  cursor: text;
`;

const StyledInput = styled.input`
  font-size: ${fontSize("default")};;
  border: none;
  outline: none;
  background-color: transparent;
  padding: ${spacing("small")};
  flex: 1;
`;

const StyledIcon = styled.span`
  padding-left: ${spacing("small")};
  display: flex;
  align-items: center;
  color: gray;
`;

const SearchIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="gray" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

export const SearchInputField = forwardRef<HTMLInputElement, SearchInputFieldProps>(
    ({ placeholder, onChange, ...props }, ref) => {
      const inputRef = useRef<HTMLInputElement | null>(null);
      const handleClick = () => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      };

      const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const inputValue  = event.target.value;
        if (onChange) {
          onChange(inputValue);
        }
      };
  
      return (
        <FrameInputField {...props}>
          <StyledInputContainer onClick={handleClick}>
            <StyledIcon>
              <SearchIcon />
            </StyledIcon>
            <StyledInput
              type="text"
              placeholder={placeholder}
              onChange={handleChange}
              ref={(el) => {
                if (ref) {
                  if (typeof ref === "function") ref(el);
                  else ref.current = el;
                }
                inputRef.current = el;
              }}
              {...props}
              />
            </StyledInputContainer>
        </FrameInputField>
      );
    }
  );