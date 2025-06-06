import { Tooltip, useTooltipScheduling } from "@protzilla/core";
import { color, duration, fontSize, fontWeight, opacity } from "@protzilla/theme";
import React, { useCallback } from "react";
import { css, styled } from "styled-components";

import { SecondaryButton } from "../button";
import { Text } from "../text";
import { SwitchOptionProps } from "./switch-option.props";

const SwitchOptionContainer = styled(SecondaryButton)<{
  isDisabled?: boolean;
  isActive?: boolean;
}>`
  cursor: ${(props) => (props.isDisabled ? "not-allowed" : "pointer")};
  min-width: 80px;
  height: 100%;
  background-color: ${(props) => color(props.isActive ? "primary" : "secondary")};
  ${(props) =>
    props.isDisabled &&
    css`
      opacity: ${opacity("disabled")};
    `}
`;

const SwitchOptionLabel = styled(Text).withConfig({
  shouldForwardProp: (prop) => prop !== "isActive",
})<{ isActive?: boolean }>`
  font-size: ${fontSize("h6")};
  line-height: ${fontSize("small")};
  font-weight: ${fontWeight("bold")};
  color: ${(props) => color(props.isActive ? "onPrimary" : "primary")};
  transition: color ${duration("short")}ms;
  white-space: nowrap;
`;

export const SwitchOption: React.FC<SwitchOptionProps> = ({
  label,
  value,
  isActive,
  isDisabled,
  onChange,
  ...rest
}) => {
  const changeHandler = useCallback(() => {
    if (onChange && !isDisabled) onChange(value);
  }, [value, isDisabled, onChange]);
  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(true);

  return (
    <SwitchOptionContainer
      {...rest}
      isDisabled={isDisabled}
      isActive={isActive}
      onPress={changeHandler}
      isShy={true}
      isSmall={true}
      onPointerEnter={handlePointerEnter}
      onPointerLeave={handlePointerLeave}
    >
      <SwitchOptionLabel isActive={isActive} text={label} />
      <Tooltip
        text={label}
        isShown={showTooltip}
        anchor={mouseAnchor}
        position="bottomRight"
        distance={13}
      />
    </SwitchOptionContainer>
  );
};
