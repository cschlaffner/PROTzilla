import React, { useEffect, useRef, useState } from "react";
import styled from "styled-components";
import type { DropdownInputFieldProps } from "./dropdown-input-field.props";
import { border, borderColors, spacing } from "../../../theme";
import { FrameInputField } from "../frame-input-field";

const DropdownContainer = styled.div`
  position: relative;
  display: inline-block;
  width: 100%;
`;

const OptionsList = styled.ul<{ width: number }>`
  position: absolute;
  width: ${({ width }) => `${width}px`};
  max-height: 150px;
  overflow-y: auto;
  background: white;
  border-radius: ${border("defaultRadius")};
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  list-style: none;
  padding: 0;
  margin-top: ${spacing("verySmall")};
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
  onClick,
  ...props
}) => {
  const [selectedValue, setSelectedValue] = useState<string>(defaultValue);
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
          <p className="selected-value-text">{selectedValue}</p>
        </FrameInputField>
      </div>

      {isOpen && (
        <OptionsList width={dropdownWidth} ref={dropdownRef}>
          {options.length > 0 ? (
            options.map((option, index) => (
              <OptionItem
                key={index}
                onClick={() => {
                  setSelectedValue(option);
                  setIsOpen(false);
                  onClick(option);
                }}
              >
                {option}
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
