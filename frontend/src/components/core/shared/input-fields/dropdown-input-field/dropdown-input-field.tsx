import { InputContainer } from "../input-container";
import { Icon } from "../../icon"
import { useOutsidePress, useToggleableState } from "@protzilla/hooks";
import { border, borderColors, color, fontSize, size, spacing } from "@protzilla/theme";
import React, { memo, useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import type { DropdownInputFieldProps } from "./dropdown-input-field.props";

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
  height: ${({ $isSmall }) => size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
  width: 100%;
`;

const OptionsList = styled.ul`
  background: white;
  border-radius: ${border("defaultRadius")};
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  list-style: none;
  margin-top: 0;
  overflow-y: auto;
  padding: 0;
  position: absolute;
  width: 100%;
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

export const DropdownInputField: React.FC<DropdownInputFieldProps> = memo(
  function DropdownInputField({ options, value, onChange, ...props }) {
    const [selectedOption, setSelectedOption] = useState(
      //TODO QUICKFIX this should be .value in the future
      options.find((option) => option.label === value) ?? options[0],
    );

    useEffect(() => {
      if (options.length === 0) {
        setSelectedOption({ label: "", value: "" });
        return;
      }

      //TODO QUICKFIX this should be .value in the future
      const initialOption = options.find((option) => option.label === value) ?? options[0];
      setSelectedOption(initialOption);

      if (initialOption.label !== value) {
        //TODO QUICKFIX this should be .value in the future
        onChange(initialOption.label); //TODO QUICKFIX this should be .value in the future
      }
      //component should only rerender on change of options because of multiple occurrences of dropdown forms
      //eslint-disable-next-line react-hooks/exhaustive-deps
    }, [options]);

    const dropdownRef = useRef<HTMLUListElement | null>(null);
    const inputRef = useRef<HTMLDivElement | null>(null);

    const [isOpen, , disable, toggle] = useToggleableState();
    useOutsidePress(
      [dropdownRef as React.RefObject<HTMLElement>, inputRef as React.RefObject<HTMLElement>],
      disable,
      isOpen,
    );

    const handleChange = (option: { label: string; value: string }) => {
      setSelectedOption(option);
      onChange(option.label); //TODO QUICKFIX this should be .value in the future
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
            inlineSuffix={<Icon icon={isOpen ? "chevronUp" : "chevronDown"} isSmall />}
          >
            <StyledInputLabel className="selected-value-text" $isSmall={props.isSmall ?? false}>
              {selectedOption.label}
            </StyledInputLabel>
          </InputContainer>
        </div>

        {isOpen && (
          <OptionsList ref={dropdownRef}>
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
  },
);
