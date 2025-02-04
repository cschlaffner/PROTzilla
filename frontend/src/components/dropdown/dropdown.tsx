import React, { useCallback, useMemo, useRef, useState } from "react";
import { css, styled } from "styled-components";

import {
  useOutsidePress,
  useScrollListener,
  useToggleableState,
} from "../../hooks";
import { FlexColumn } from "../box";
import { ToggleableButton } from "../button";
import { Icon, iconColor } from "../icon";
import { InputLabel } from "../text";
import { TextField } from "../text-field";
import { DropdownOption, DropdownOptions } from "./dropdown-options";
import { DropdownProps } from "./dropdown.props";
import { useTranslation } from "../../i18n";
import { fontSize, size } from "../../theme";

const Container = styled(FlexColumn)<{ isCentered?: boolean }>`
  align-items: stretch;
`;

const Selector = styled(DropdownOption)`
  border-radius: 6px;
  position: relative;
`;

const StyledTextField = styled(TextField)`
  width: 100%;

  .input {
    padding-left: 20px;
    font-size: 13px;
  }
`;

const SelectedOption = styled(ToggleableButton)<{
  isDSmall?: boolean;
  isDisabled?: boolean;
}>`
  width: 100%;
  justify-content: space-between;
  text-align: left;

  ${(props) =>
    props.isDSmall &&
    css`
      height: ${size("smallDropdownHeight")};
      min-height: ${size("smallDropdownHeight")};

      .text {
        font-size: ${fontSize("default")};
      }
    `}

  .icon {
    ${({ isDisabled, isActive }) =>
      iconColor(
        isDisabled ? "primaryDisabled" : isActive ? "onPrimary" : "text",
      )};
  }

  .text {
    white-space: normal;
    word-wrap: break-word;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;

const ExpandIcon = styled(Icon)`
  margin-right: 0px;
`;

export const Dropdown: React.FC<DropdownProps> = ({
  value,
  defaultValue,
  options,
  label: label,
  labelTx,
  labelComponents,
  labelData,
  placeholder,
  placeholderTx,
  placeholderData,
  isDisabled,
  isSearchable,
  isOtherAllowed,
  isOtherSelected,
  isSmall,
  otherLabelTx,
  otherLabelComponents,
  otherLabelData,
  defaultOther = "",
  marqueeTextLength,
  autoFocus,
  onOtherChange,
  onChange,
  onSearch,
  ...rest
}) => {
  const { t } = useTranslation();

  const actualValue = value === undefined ? defaultValue : value;

  const activeOptionIndex = options.findIndex(
    (option) => option.value === actualValue,
  );

  const activeOption =
    activeOptionIndex >= 0 ? options[activeOptionIndex] : undefined;

  const [isOpen, open, close] = useToggleableState();

  const [isSearching, startSearching, stopSearching] = useToggleableState();
  const searchRef = useRef<HTMLInputElement>(null);

  const onOpen = useCallback(() => {
    open();
    if (isSearchable) {
      startSearching();
      searchRef.current?.focus();
    }
  }, [isSearchable, open, startSearching]);

  const onClose = useCallback(() => {
    close();
    if (isSearching) {
      stopSearching();
    }
  }, [close, isSearching, stopSearching]);

  const setValue = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (newValue: any, shouldCloseOnChange = true) => {
      if (shouldCloseOnChange) onClose();
      onChange?.(newValue);
    },
    [onChange, onClose],
  );

  const handleKey = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === "ArrowUp") {
        event.preventDefault();
        setValue(
          options[
            (options.length + activeOptionIndex - 1) %
              Math.max(1, options.length)
          ]?.value,
          false,
        );
      } else if (event.key === "ArrowDown") {
        event.preventDefault();
        setValue(
          options[(activeOptionIndex + 1) % Math.max(1, options.length)]?.value,
          false,
        );
      } else if (event.key === "Enter") {
        event.preventDefault();
        setValue(options[activeOptionIndex]?.value, true);
      }
    },
    [activeOptionIndex, options, setValue],
  );

  const optionsRef = useRef<HTMLDivElement>(null);
  const selectorRef = useRef<HTMLDivElement>(null);

  const handleScroll = useCallback(
    (event: Event) => {
      if (optionsRef.current?.contains(event.target as Node)) return;
      onClose();
    },
    [onClose],
  );
  useScrollListener(handleScroll, isOpen);

  const refs = useMemo(() => [selectorRef, optionsRef], []);
  useOutsidePress(refs, onClose, isOpen);

  const [other, setOther] = useState(defaultOther);

  return (
    <Container {...rest}>
      {(labelTx ?? label) && (
        <InputLabel
          className="label"
          tx={labelTx}
          text={label}
          txComponents={labelComponents}
          txData={labelData}
          isDisabled={isDisabled}
        />
      )}
      <Selector className="selector" ref={selectorRef}>
        {isOtherSelected && isOtherAllowed ? (
          <SelectedOption
            text={other}
            isActive={isOpen}
            className="select-button"
            isDSmall={isSmall}
            isDisabled={isDisabled}
            autoFocus={autoFocus}
            onPress={isOpen ? onClose : onOpen}
            onKeyDown={handleKey}
          >
            <ExpandIcon
              className="icon"
              icon={isOpen ? "chevronUp" : "chevronDown"}
            />
          </SelectedOption>
        ) : isSearchable && isSearching ? (
          <StyledTextField
            autoFocus
            value={
              activeOption?.labelTx
                ? t(activeOption.labelTx)
                : activeOption
                  ? String(
                      activeOption.label
                        ? activeOption.label
                        : activeOption.value,
                    )
                  : ""
            }
            onKeyDown={handleKey}
            onChangeText={onSearch}
            onConfirm={stopSearching}
            placeholderTx={placeholderTx}
            placeholder={placeholder}
            placeholderData={placeholderData}
            ref={searchRef}
            isDisabled={isDisabled}
          />
        ) : (
          <SelectedOption
            className="select-button"
            tx={activeOption ? activeOption.labelTx : placeholderTx}
            text={
              (activeOption
                ? (activeOption.label ?? String(activeOption.value))
                : placeholder) ?? ""
            }
            txComponents={activeOption?.labelComponents}
            txData={activeOption ? activeOption.labelData : placeholderData}
            isActive={isOpen}
            isDSmall={isSmall}
            isDisabled={isDisabled}
            autoFocus={autoFocus}
            onKeyDown={handleKey}
            onPress={isOpen ? onClose : onOpen}
          >
            <ExpandIcon
              className="icon"
              icon={isOpen ? "chevronUp" : "chevronDown"}
            />
          </SelectedOption>
        )}

        {isOpen && (
          <DropdownOptions
            options={options}
            isOtherSelected={isOtherSelected}
            isSmall={isSmall}
            isDisabled={isDisabled}
            isOtherAllowed={isOtherAllowed}
            other={other}
            setOther={setOther}
            onOtherChange={onOtherChange}
            otherLabelTx={otherLabelTx}
            otherLabelComponents={otherLabelComponents}
            otherLabelData={otherLabelData}
            activeOptionIndex={activeOptionIndex}
            setValue={setValue}
            anchor={selectorRef.current}
            ref={optionsRef}
            marqueeTextLength={marqueeTextLength}
          />
        )}
      </Selector>
    </Container>
  );
};
