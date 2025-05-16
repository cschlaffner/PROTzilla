import { color, duration, opacity, radius } from "@protzilla/theme";
import { UIStateProps } from "@protzilla/utils";
import React from "react";
import { css, styled } from "styled-components";

import { SwitchOption } from "./switch-option";
import { SwitchProps } from "./switch.props";

const SwitchContainer = styled.div`
  border-radius: ${radius("button")};
  flex-direction: row;
  position: relative;
  user-select: none;
  background-color: ${color("secondary")};
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ActiveSwitchOption = styled.div<UIStateProps>`
  height: 100%;
  transition: left ${duration("short")}ms;
  position: absolute;
  border-radius: ${radius("button")};
  background-color: ${color("primary")};
  display: flex;

  ${(props) =>
    props.isDisabled &&
    css`
      opacity: ${opacity("disabled")};
    `}
`;

export const Switch: React.FC<SwitchProps> = ({
  value,
  options,
  onChange,
  defaultValue,
  isDisabled,
  ...rest
}) => {
  const { length } = options;
  const actualValue =
    value === undefined ? defaultValue || (length ? options[0].value : "") : value;

  const activeIndex = Math.max(
    0,
    options.findIndex((option) => option.value === actualValue),
  );

  return (
    <SwitchContainer {...rest}>
      {length && (
        <>
          <ActiveSwitchOption
            isDisabled={isDisabled}
            style={{
              width: `${String(100 / length)}%`,
              left: `${String((100 / length) * activeIndex)}%`,
            }}
          />
          {options.map(({ value: itemValue, isDisabled: isItemDisabled, ...itemRest }, index) => (
            <SwitchOption
              isActive={index === activeIndex}
              key={itemValue}
              onChange={onChange}
              value={itemValue}
              isDisabled={isItemDisabled ?? isDisabled}
              {...itemRest}
            />
          ))}
        </>
      )}
    </SwitchContainer>
  );
};
