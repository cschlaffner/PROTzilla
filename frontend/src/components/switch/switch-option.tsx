import React, { useCallback } from "react";
import { css, styled } from "styled-components";

import { Button } from "../button";
import { Text } from "../text";
import { SwitchOptionProps } from "./switch-option.props";
import { color, duration, fontSize, fontWeight, opacity } from "../../theme";

const SwitchOptionContainer = styled(Button)<{
  isDisabled?: boolean;
}>`
  cursor: ${(props) => (props.isDisabled ? "not-allowed" : "pointer")};
  flex: 1;
  width: 80px;
  height: 100%;

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
`;

export const SwitchOption: React.FC<SwitchOptionProps> = ({
  labelTx,
  label,
  labelComponents,
  labelData,
  value,
  isActive,
  isDisabled,
  onChange,
  ...rest
}) => {
  const changeHandler = useCallback(() => {
    if (onChange && !isDisabled) onChange(value);
  }, [value, isDisabled, onChange]);

  return (
    <SwitchOptionContainer
      {...rest}
      isDisabled={isDisabled}
      onPress={changeHandler}
      isShy={true}
      isSmall={true}
    >
      <SwitchOptionLabel
        isActive={isActive}
        tx={labelTx}
        txComponents={labelComponents}
        txData={labelData}
        text={label ?? value}
      />
    </SwitchOptionContainer>
  );
};
