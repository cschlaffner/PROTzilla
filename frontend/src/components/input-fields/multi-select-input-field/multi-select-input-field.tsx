import React, { useEffect, useState } from "react";
import { styled } from "styled-components";

import { MultiSelectInputFieldProps } from "./multi-select-input-field.props";
import { border, borderColors, color, size, spacing } from "../../../theme";
import { FlexColumn, FlexRow } from "../../box";
import { Icon } from "../../icon";
import { InputLabel } from "../../text";
import { FrameInputField } from "../frame-input-field";
import { SearchInputField } from "../search-input-field";

const OptionsListContainer = styled.ul`
  border-radius: ${border("defaultRadius")};
  border: ${border("smallStrength")} solid ${borderColors("default")};
  height: ${size("inputFieldListSmall")};
  list-style: none;
  margin: ${spacing("verySmall")} 0 ${spacing("small")} 0;
  overflow-y: auto;
  padding: 0;
  width: 100%;
`;

const OptionItem = styled.li`
  &:hover {
    background: ${color("gray6")};
  }
  align-items: center;
  display: flex;
  justify-content: space-between;
  padding: ${spacing("verySmall")} ${spacing("small")};
  position: relative;
  user-select: none;
`;

const ListLabel = styled(InputLabel)``;

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
              onClick={() => {
                onItemClick(option);
              }}
              style={{ cursor: "pointer" }}
            >
              {isLeftList ? (
                <>
                  <span>{option.label}</span>
                  <Icon icon="chevronRight" isSmall />
                </>
              ) : (
                <>
                  <Icon icon="chevronLeft" isSmall />
                  <span>{option.label}</span>
                </>
              )}
            </OptionItem>
          ))
        ) : (
          <OptionItem style={{ pointerEvents: "none" }}>No entry</OptionItem>
        )}
      </OptionsListContainer>
    </div>
  );
};

export const MultiSelectInputField: React.FC<MultiSelectInputFieldProps> = ({
  options,
  defaultOptions = [],
  onChange,
  ...props
}) => {
  const [selectedOptions, setSelectedOptions] = useState<
    { label: string; value: string }[]
  >([]);
  const [searchTerm, setSearchTerm] = useState<string>("");

  const sortOptions = (options: { label: string; value: string }[]) =>
    [...options].sort((a, b) => a.value.localeCompare(b.value));

  useEffect(() => {
    const initialSelected = options.filter((opt) =>
      defaultOptions.includes(opt.value),
    );
    const sortedSelection = sortOptions(initialSelected);
    setSelectedOptions(sortedSelection);
    onChange(sortedSelection.map((opt) => opt.value));
  }, [options, defaultOptions, onChange]);

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

      const sortedSelection = sortOptions(newSelection);
      setSelectedOptions(sortedSelection);
      onChange(sortedSelection.map((opt) => opt.value));
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
            defaultValue={searchTerm}
            onChange={(e) => {
              setSearchTerm(e);
            }}
            placeholder="Search in lists"
            smallBorder={true}
            smallFrame={true}
          />
        </div>
      </FlexColumn>
    </FrameInputField>
  );
};
