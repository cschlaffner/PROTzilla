import { radius } from "@protzilla/theme";
import React from "react";
import { styled } from "styled-components";

import { SwitchOption } from "./switch-option";
import { SwitchProps } from "./switch.props";

const SwitchContainer = styled.div`
  border-radius: ${radius("button")};
  flex-direction: row;
  position: relative;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
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
    value === undefined ? (defaultValue ?? (length ? options[0].value : "")) : value;

  const activeIndex = Math.max(
    0,
    options.findIndex((option) => option.value === actualValue),
  );

  return (
    <SwitchContainer {...rest}>
      {length && (
        <>
          {options.map(({ value: itemValue, isDisabled: isItemDisabled, ...itemRest }, index) => {
            const optionKey =
              typeof itemValue === "string" || typeof itemValue === "number"
                ? itemValue
                : `${itemRest.label ?? "option"}-${String(index)}`;

            return (
              <SwitchOption
                isActive={index === activeIndex}
                key={optionKey}
                onChange={onChange}
                value={itemValue}
                isDisabled={isItemDisabled ?? isDisabled}
                {...itemRest}
              />
            );
          })}
        </>
      )}
    </SwitchContainer>
  );
};
