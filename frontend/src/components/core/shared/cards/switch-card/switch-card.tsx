import { shadow, spacing } from "@protzilla/theme";
import { SwitchComponent } from "@protzilla/utils";
import React, { useEffect, useState } from "react";
import { styled } from "styled-components";

import { SwitchCardProps } from "./switch-card.props";
import { Switch } from "../../switch";
import { Card } from "../card";

const SwitchDiv = styled.div<{ hasSwitchAlignStart: boolean }>`
  display: flex;
  justify-content: ${({ hasSwitchAlignStart }) =>
    hasSwitchAlignStart ? "flex-start" : "flex-end"};
  padding-bottom: ${spacing("small")};
`;

const StyledCard = styled(Card)<{ hasShadow: boolean }>`
  box-shadow: ${({ hasShadow }) => (hasShadow ? shadow("box_shadow") : "none")};
`;

export const SwitchCard: React.FC<SwitchCardProps> = ({
  components,
  hasSwitchAlignStart = true,
  hasCardTitle = true,
  hasShadow = true,
  styleProps,
  selection = undefined,
  callback = undefined,
}) => {
  const [switchState, setSwitchState] = useState<SwitchComponent>({ name: "Error", value: <></> });

  useEffect(() => {
    const selectedComponent = selection
      ? components.find((component) => component.name === selection)
      : components[0];
    const fallbackComponent =
      components.length > 0 ? components[0] : { name: "Error", value: <></> };
    setSwitchState(selectedComponent ?? fallbackComponent);
  }, [components, selection]);

  const setSwitchStateWrapper = (newSelection: SwitchComponent) => {
    if (callback) callback(newSelection);
    setSwitchState(newSelection);
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "auto",
        ...(styleProps ?? {}),
      }}
    >
      <SwitchDiv hasSwitchAlignStart={hasSwitchAlignStart}>
        <Switch
          options={components.map((component) => ({ value: component, label: component.name }))}
          value={switchState}
          onChange={setSwitchStateWrapper}
        />
      </SwitchDiv>
      <StyledCard
        hasShadow={hasShadow}
        {...(hasCardTitle
          ? {
              title: switchState.name,
            }
          : {})}
      >
        {switchState.value}
      </StyledCard>
    </div>
  );
};
