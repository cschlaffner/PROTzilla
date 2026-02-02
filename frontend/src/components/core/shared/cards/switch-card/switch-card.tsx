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

const FALLBACK_COMPONENT: SwitchComponent = { name: "Error", value: <></> };

const getSelectedName = (items: SwitchComponent[], selectedName?: string) => {
  if (selectedName) {
    const selectedComponent = items.find((component) => component.name === selectedName);
    if (selectedComponent) return selectedComponent.name;
  }
  return items.length > 0 ? items[0].name : FALLBACK_COMPONENT.name;
};

export const SwitchCard: React.FC<SwitchCardProps> = ({
  components,
  hasSwitchAlignStart = true,
  hasCardTitle = true,
  hasShadow = true,
  styleProps,
  selection = undefined,
  callback = undefined,
}) => {
  const [switchStateName, setSwitchStateName] = useState<string>(() =>
    getSelectedName(components, selection),
  );

  useEffect(() => {
    setSwitchStateName(getSelectedName(components, selection));
  }, [components, selection]);

  const setSwitchStateWrapper = (newSelectionName: SwitchComponent["name"]) => {
    const selectedComponent = components.find((component) => component.name === newSelectionName);
    if (selectedComponent && callback) callback(selectedComponent);
    setSwitchStateName(newSelectionName);
  };

  const activeComponent =
    components.find((component) => component.name === switchStateName) ??
    (components.length > 0 ? components[0] : FALLBACK_COMPONENT);

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
          options={components.map((component) => ({
            value: component.name,
            label: component.name,
          }))}
          value={switchStateName}
          onChange={setSwitchStateWrapper}
        />
      </SwitchDiv>
      <StyledCard
        hasShadow={hasShadow}
        {...(hasCardTitle
          ? {
              title: activeComponent.name,
            }
          : {})}
      >
        {activeComponent.value}
      </StyledCard>
    </div>
  );
};
