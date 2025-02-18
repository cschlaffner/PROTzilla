import React, { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import { border, borderColors, size, spacing } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import type { DropdownInputFieldProps } from "./dropdown-input-field.props";

const DropdownContainer = styled.div`
  display: inline-block;
  position: relative;
  width: 100%;
`;

const OptionsList = styled.ul<{ width: number }>`
  background: white;
  border-radius: ${border("defaultRadius")};
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  list-style: none;
  margin-top: ${spacing("verySmall")};
  max-height: ${size("inputFieldListSmall")};
  overflow-y: auto;
  padding: 0;
  position: absolute;
  width: ${({ width }) => `${width.toString()}px`};
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

const DropdownIcon = () => (
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
    <path d="M6 9l6 6 6-6" />
  </svg>
);

export const DropdownInputField: React.FC<DropdownInputFieldProps> = ({
  options,
  defaultValue = options[0],
  onChange,
  ...props
}) => {
  const [selectedValue, setSelectedValue] = useState<{ label: string; value: string }>(defaultValue);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLUListElement | null>(null);
  const inputRef = useRef<HTMLDivElement | null>(null);
  const [dropdownWidth, setDropdownWidth] = useState<number>(200);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    if (inputRef.current) {
      setDropdownWidth(inputRef.current.getBoundingClientRect().width);
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleChange = (option: { label: string; value: string }) => {
    setSelectedValue(option);
    onChange(option.value);
    setIsOpen(false);
  };

  const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement;
    if (
      target.closest(".inline-prefix") ||
      target.closest(".inline-suffix") ||
      target.closest(".selected-value-text")
    ) {
      setIsOpen(!isOpen);
    }
  };

  return (
    <DropdownContainer>
      <div ref={inputRef} onClick={handleClick}>
        <FrameInputField {...props} inlineSuffix={<DropdownIcon />}>
          <p className="selected-value-text">{selectedValue.label}</p>
        </FrameInputField>
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
