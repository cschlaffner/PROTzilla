import React, { useState } from "react";
import styled from "styled-components";
import type { DropdownInputFieldProps } from "./dropdown-input-field.props";
import { TextInputField } from "../text-input-field";

const DropdownContainer = styled.div`
  position: relative;
  display: inline-block;
  width: 200px; /* Setzt eine feste Breite */
`;

const OptionsList = styled.ul`
  position: absolute;
  width: inherit; /* Nimmt exakt die Breite von DropdownContainer */
  max-height: 150px;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #ccc;
  list-style: none;
  padding: 0;
  margin-top: 4px;
  z-index: 1000;
`;

const OptionItem = styled.li`
  padding: 10px;
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
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="gray" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9l6 6 6-6" />
  </svg>
);


export const DropdownInputField: React.FC<DropdownInputFieldProps> = ({
  options,
  value,
  defaultValue = "",
  onSelect,
  placeholder = "Search...",
  ... props
}) => {
  const [searchTerm, setSearchTerm] = useState<string>(value ?? defaultValue);
  const [isOpen, setIsOpen] = useState(false);

  const filteredOptions = options.filter((option) =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelect = (selectedValue: string) => {
    setSearchTerm(selectedValue);
    setIsOpen(false);
    onSelect(selectedValue);
  };

  return (
    <DropdownContainer>
      <TextInputField
        value={searchTerm}
        onChange={setSearchTerm}
        placeholder={placeholder}
        inlineSuffix={<DropdownIcon />}
        onFocus={() => setIsOpen(true)}
        {...props}
      />
      {isOpen && (
        <OptionsList>
          {filteredOptions.length > 0 ? (
            filteredOptions.map((option, index) => (
              <OptionItem key={index} onClick={() => handleSelect(option)}>
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
