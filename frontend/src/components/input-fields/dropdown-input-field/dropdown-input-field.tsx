import React, { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import {
  border,
  borderColors,
  color,
  fontSize,
  size,
  spacing,
} from "../../../theme";
import { InputContainer } from "../frame-input-field";
import type { DropdownInputFieldProps } from "./dropdown-input-field.props";
import { useOutsidePress } from "../../../hooks/outside-press";
import { useToggleableState } from "../../../hooks/toggleable-state";
import { Icon } from "../../icon";

const DropdownContainer = styled.div`
  display: inline-block;
  position: relative;
  width: 100%;
`;

const StyledInputLabel = styled.p<{ $isSmall: boolean }>`
  font-size: ${fontSize("default")};
  display: flex;
  align-items: center;
  padding: 0px ${spacing("small")};
  background: ${color("transparent")};
  border: none;
  outline: none;
  height: ${({ $isSmall }) =>
    size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

const OptionsList = styled.ul<{ width: number }>`
  background: white;
  border-radius: ${border("defaultRadius")};
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  list-style: none;
  margin-top: 0;
  overflow-y: auto;
  padding: 0;
  position: absolute;
 // width: ${({ width }) => `${width.toString()}px`};
  width: 500px;
  z-index: 1000;
`;

const OptionItem = styled.li`
  padding: ${spacing("small")};
  cursor: pointer;
  transition: background 0.2s ease-in-out;
  position: relative;

  &::after {
    content: "";
    position: absolute;
    left: 5%;
    right: 5%;
    bottom: 0;
    height: 1px;
    background: linear-gradient(
      to right,
      rgba(200, 200, 200, 0.1) 0%,
      rgba(200, 200, 200, 0.3) 50%,
      rgba(200, 200, 200, 0.1) 100%
    );
  }

  &:hover {
    background: #f5f5f5;
  }

  &:last-child::after {
    display: none;
  }
`;

export const DropdownInputField: React.FC<DropdownInputFieldProps> = ({
  options,
  value,
  onChange,
  ...props
}) => {
  const [selectedValue, setSelectedValue] = useState(() => {
    const initialValue =
      options.find((option) => option.value === value) ?? options[0];
    onChange(initialValue.value);
    return initialValue;
  });

  const dropdownRef = useRef<HTMLUListElement | null>(null);
  const inputRef = useRef<HTMLDivElement | null>(null);
  const [dropdownWidth, setDropdownWidth] = useState<number>(200);

  const [isOpen, , disable, toggle] = useToggleableState();
  useOutsidePress(
    [
      dropdownRef as React.RefObject<HTMLElement>,
      inputRef as React.RefObject<HTMLElement>,
    ],
    disable,
    isOpen,
  );

  useEffect(() => {
    if (inputRef.current) {
      setDropdownWidth(inputRef.current.getBoundingClientRect().width);
    }
  }, []);

  const handleChange = (option: { label: string; value: string }) => {
    setSelectedValue(option);
    onChange(option.value);
    disable();
  };

  const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement;
    if (
      target.closest(".inline-prefix") ||
      target.closest(".inline-suffix") ||
      target.closest(".selected-value-text")
    ) {
      toggle();
    }
  };

  return (
    <DropdownContainer>
      <div ref={inputRef} onClick={handleClick}>
        <InputContainer
          {...props}
          inlineSuffix={
            <Icon icon={isOpen ? "chevronUp" : "chevronDown"} isSmall />
          }
        >
          <StyledInputLabel
            className="selected-value-text"
            $isSmall={props.isSmall ?? false}
          >
            {selectedValue.label}
          </StyledInputLabel>
        </InputContainer>
      </div>

      {isOpen && (
        <OptionsList width={dropdownWidth} ref={dropdownRef}>
          {options.length > 0 ? (
            options.map((option) => (
              <OptionItem
                key={option.value}
                onClick={() => {
                  handleChange(option);
                }}
              >
                {option.label}
              </OptionItem>
            ))
          ) : (
            <OptionItem>No results</OptionItem>
          )}
        </OptionsList>
      )}
    </DropdownContainer>
  );
};
