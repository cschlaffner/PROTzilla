import { spacing } from "@protzilla/theme";
import { SwitchComponent } from "@protzilla/utils";
import React, { useEffect, useState } from "react";
import { styled } from "styled-components";

import { SwitchCardProps } from "./switch-card.props";
import { Switch } from "../../switch";
import { Card } from "../card";

const SwitchDiv = styled.div<{ hasSwitchAlginStart: boolean }>`
  display: flex;
  justify-content: ${({ hasSwitchAlginStart }) =>
    hasSwitchAlginStart ? "flex-start" : "flex-end"};
  padding-bottom: ${spacing("small")};
`;

export const SwitchCard: React.FC<SwitchCardProps> = ({
  components,
  hasSwitchAlginStart = true,
  hasCardTitle = true,
  styleProps,
}) => {
  const [switchState, setSwitchState] = useState<SwitchComponent>({ name: "Error", value: <></> });

  useEffect(() => {
    setSwitchState(components[0]);
  }, [components]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "auto",
        ...(styleProps ?? {}),
      }}
    >
      <SwitchDiv hasSwitchAlginStart={hasSwitchAlginStart}>
        <Switch
          options={components.map((component) => ({ value: component, label: component.name }))}
          value={switchState}
          onChange={setSwitchState}
        />
      </SwitchDiv>
      <Card
        {...(hasCardTitle
          ? {
              title: switchState.name,
            }
          : {})}
      >
        {switchState.value}
      </Card>
    </div>
  );
};
