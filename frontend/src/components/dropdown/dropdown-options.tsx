import { t } from "i18next";
import React, { useCallback } from "react";
import ReactDOM from "react-dom";
import { css, styled } from "styled-components";

import { ToggleableButton, ToggleableButtonProps } from "../button";
import { Text, TextProps } from "../text";
import { TextField } from "../text-field";
import { DropdownOptionsProps } from "./dropdown.props";
import { useFloatingPosition } from "./utils";
import { useModalRoot } from "../../hooks";
import {
  color,
  fontSize,
  fontWeight,
  radius,
  size,
  spacing,
  zIndex,
} from "../../theme";
import { UIStateProps } from "../types";

export const DropdownOption = styled.div<{ enableMarquee?: boolean }>`
  width: 100%;
  align-items: center;
  box-sizing: border-box;
  cursor: pointer;
  display: flex;
  overflow: visible;
  user-select: none;

  ${({ enableMarquee }) =>
    enableMarquee &&
    css`
      :hover {
        .text {
          width: 100vw;
          align-items: center;
          position: absolute;
          animation: marquee 6s linear infinite;
          animation-delay: -3s;
          margin-left: 20px;
        }
      }
    `}

  @keyframes marquee {
    0% {
      left: 100%;
    }
    50% {
      left: 0;
    }
    100% {
      left: -100%;
    }
  }
`;

const OptionsContainer = styled.div`
  position: absolute;
  max-height: 200px;
  background: ${color("secondary")};
  box-sizing: border-box;
  border-radius: ${radius("button")};
  z-index: ${zIndex("modal")};
  overflow-y: auto;
  pointer-events: auto;
`;

const StandardOptionsContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
`;

const OptionContent = styled(ToggleableButton)<
  Pick<ToggleableButtonProps, "isActive"> & { isDSmall?: boolean }
>`
  border-radius: 0;
  width: 100%;
  display: flex;
  justify-content: left;
  text-align: left;
  overflow: hidden;

  .text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    position: relative;
  }

  ${(props) =>
    props.isDSmall &&
    css`
      height: ${size("smallDropdownHeight")};
      min-height: ${size("smallDropdownHeight")};

      .text {
        font-size: ${fontSize("default")};
      }
    `}
`;

const OtherOptionContainer = styled.div<
  Pick<ToggleableButtonProps, "isActive"> & UIStateProps
>`
  align-items: center;
  background-color: ${({ isActive, isDisabled }) =>
    color(isActive && !isDisabled ? "primary" : "secondary")};
  box-sizing: border-box;
  cursor: pointer;
  display: flex;
  overflow: hidden;
  height: 54px;
  padding: ${spacing("buttonPadding")};
  justify-content: space-between;

  :hover {
    background-color: ${({ isActive, isDisabled }) =>
      color(
        isDisabled ? "secondary" : isActive ? "primaryHover" : "secondaryHover",
      )};
  }

  :active {
    background-color: ${({ isActive, isDisabled }) =>
      color(
        isDisabled
          ? "secondary"
          : isActive
            ? "primaryActive"
            : "secondaryActive",
      )};
  }

  .text {
    font-size: ${fontSize("button")};
    font-weight: ${fontWeight("bold")};
    color: ${({ isActive, isDisabled }) =>
      color(
        isDisabled ? "primaryDisabled" : isActive ? "onPrimary" : "primary",
      )};
  }
`;

export const OtherOptionText = styled(Text)<Pick<TextProps, "isDisabled">>`
  font-size: ${fontSize("button")};
  font-weight: ${fontWeight("bold")};
  color: ${({ isDisabled }) =>
    color(isDisabled ? "primaryDisabled" : "primary")};
  margin-bottom: 2px;
`;

const OtherOptionTextField = styled(TextField)`
  background-color: ${color("background")};
  border-radius: 6px;
  margin-left: 10px;
  height: 30px;

  .input {
    max-width: 220px;
    height: 30px;
  }
`;

export const DropdownOptions = React.forwardRef<
  HTMLDivElement,
  DropdownOptionsProps
>(function DropdownOptions(
  {
    options,
    isOtherSelected,
    activeOptionIndex,
    isSmall,
    isDisabled,
    isOtherAllowed,
    other,
    setOther,
    otherLabelComponents,
    otherLabelData,
    otherLabelTx,
    onOtherChange,
    setValue,
    anchor,
    marqueeTextLength,
  },
  ref,
) {
  const modalRootRef = useModalRoot();

  const floatStyle = useFloatingPosition({
    anchor,
    isActive: true,
    distance: 10,
  });

  const onOtherEdit = useCallback(
    (newOther: string) => {
      setOther(newOther);
      onOtherChange?.(newOther);
    },
    [onOtherChange, setOther],
  );

  const activateOther = useCallback(() => {
    if (other) onOtherChange?.(other);
  }, [onOtherChange, other]);

  const node = (
    <OptionsContainer className="options" style={floatStyle} ref={ref}>
      <StandardOptionsContainer>
        {options.map((option, index) => (
          <DropdownOption
            key={
              typeof option.value === "string" ||
              typeof option.value === "number"
                ? String(option.value)
                : index
            }
            enableMarquee={
              marqueeTextLength
                ? (
                    (option.labelTx
                      ? t(option.labelTx)
                      : (option.label ?? String(option.value))) as string
                  ).length >= marqueeTextLength
                : undefined
            }
          >
            <OptionContent
              tx={option.labelTx}
              text={option.label ?? String(option.value)}
              txComponents={option.labelComponents}
              txData={option.labelData}
              onPress={() => {
                setValue(option.value);
              }}
              className="option"
              isDSmall={isSmall}
              isActive={!isOtherSelected && index === activeOptionIndex}
              isDisabled={isDisabled}
            />
          </DropdownOption>
        ))}
      </StandardOptionsContainer>

      {(isOtherAllowed ?? isOtherSelected) && (
        <OtherOptionContainer
          isActive={isOtherSelected}
          onPointerDown={activateOther}
          isDisabled={!isOtherAllowed}
        >
          <OtherOptionText
            className="text"
            tx={otherLabelTx ?? "base:otherSelectionOption"}
            txComponents={otherLabelComponents}
            txData={otherLabelData}
          />
          <OtherOptionTextField value={other} onChangeText={onOtherEdit} />
        </OtherOptionContainer>
      )}
    </OptionsContainer>
  );

  return modalRootRef.current
    ? ReactDOM.createPortal(node, modalRootRef.current)
    : node;
});
