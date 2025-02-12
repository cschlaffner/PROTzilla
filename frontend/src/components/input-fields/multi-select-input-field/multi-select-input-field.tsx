import React, { forwardRef, useEffect, useState } from "react";
import styled from "styled-components";
import { FrameInputField } from "../frame-input-field";
import { border, borderColors, fontSize, spacing } from "../../../theme";
import { MultiSelectInputFieldProps } from "./multi-select-input-field.props";
import { FlexColumn, FlexRow } from "../../box";
import { SearchInputField } from "../search-input-field";
import { InputLabel, Text } from "../../text";

const OptionsListContainer = styled.ul`
  //position: absolute;
  height: 100px;
  width: 100%;
  overflow-y: auto;
  list-style: none;
  border: ${border("smallStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  // box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
  padding: 0;
  margin: ${spacing("verySmall")} 0 ${spacing("small")} 0;
`;

const OptionItem = styled.li`
  padding: ${spacing("verySmall")} ${spacing("small")};
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
  &:hover {
    background: #f5f5f5;
  }
`;

const ListLabel = styled(InputLabel)``;

const LeftCaretIcon = () => (
  <svg
    width="10"
    height="10"
    viewBox="0 0 10 10"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M7 2L3 5L7 8"
      stroke="black"
      strokeWidth="1"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const RightCaretIcon = () => (
  <svg
    width="10"
    height="10"
    viewBox="0 0 10 10"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M3 2L7 5L3 8"
      stroke="black"
      strokeWidth="1"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const OptionsListComponent: React.FC<{
  titleLabel: string;
  optionsList: { label: string; value: string }[];
  searchTerm: string;
  onItemClick: (option: { label: string; value: string }) => void;
  isLeftList: boolean;
}> = ({ titleLabel, optionsList, searchTerm, onItemClick, isLeftList }) => {
  const filteredOptions = optionsList.filter((option) =>
    option.label.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div style={{ width: "100%" }}>
      <ListLabel text={titleLabel} />
      <OptionsListContainer>
        {filteredOptions.length > 0 ? (
          filteredOptions.map((option) => (
            <OptionItem
              key={option.value}
              onClick={() => onItemClick(option)}
              style={{ cursor: "pointer" }}
            >
              {isLeftList ? (
                <>
                  <span>{option.label}</span>
                  <RightCaretIcon />
                </>
              ) : (
                <>
                  <LeftCaretIcon /> <span>{option.label}</span>
                </>
              )}
            </OptionItem>
          ))
        ) : (
          <OptionItem style={{ pointerEvents: "none"}}>No entry</OptionItem>
        )}
      </OptionsListContainer>
    </div>
  );
};

export const MultiSelectInputField = forwardRef<
  HTMLInputElement,
  MultiSelectInputFieldProps
>(({ options, onChange, ...props }, ref) => {
  const [selectedOptions, setSelectedOptions] = useState<
    { label: string; value: string }[]
  >([]);
  const [searchTerm, setSearchTerm] = useState<string>("");

  const unselectedOptions = options.filter(
    (option) =>
      !selectedOptions.some((selected) => selected.value === option.value),
  );

  const handleItemClick = (option: { label: string; value: string }) => {
    setSelectedOptions((prev) => {
      const newSelection = prev.some(
        (selected) => selected.value === option.value,
      )
        ? prev.filter((item) => item.value !== option.value)
        : [...prev, option];

      onChange(newSelection.map((opt) => opt.value));
      return newSelection;
    });
  };
  return (
    <FrameInputField {...props}>
      <FlexColumn style={{ width: "100%" }}>
        <FlexRow style={{ width: "100%", gap: "10px" }}>
          <OptionsListComponent
            titleLabel="Unselected:"
            optionsList={unselectedOptions}
            searchTerm={searchTerm}
            onItemClick={handleItemClick}
            isLeftList={true}
          />
          <OptionsListComponent
            titleLabel="Selected:"
            optionsList={selectedOptions}
            searchTerm={searchTerm}
            onItemClick={handleItemClick}
            isLeftList={false}
          />
        </FlexRow>
        <div style={{ width: "100%" }}>
          <SearchInputField
            style={{ padding: "0", gap: "0" }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e)}
            placeholder="Search in lists"
            smallBorder={true}
          />
        </div>
      </FlexColumn>
    </FrameInputField>
  );
});
