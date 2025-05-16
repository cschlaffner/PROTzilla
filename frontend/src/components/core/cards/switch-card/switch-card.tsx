import { Card, Switch} from "@protzilla/core";
import { spacing } from "@protzilla/theme";
import React, { useState } from "react";
import { styled } from "styled-components";

import { SwitchCardProps } from "./switch-card.props";

const SwitchDiv = styled.div<{ hasSwitchAlginStart: boolean }>`
  display: flex;
  justify-content: ${({ hasSwitchAlginStart }) =>
    hasSwitchAlginStart ? "flex-start" : "flex-end"};
  padding-bottom: ${spacing("small")};
`;

export const SwitchCard: React.FC<SwitchCardProps> = ({
  nameComponent1,
  component1,
  nameComponent2,
  component2,
  hasSwitchAlginStart = true,
  hasCardTitle = true,
  styleProps,
}) => {
  const [switchState, setSwitchState] = useState<string>("component1");

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
          options={[
            { value: "component1", label: nameComponent1 },
            { value: "component2", label: nameComponent2 },
          ]}
          value={switchState}
          onChange={setSwitchState}
          defaultValue="component1"
        />
      </SwitchDiv>
      <Card
        {...(hasCardTitle
          ? {
              title: switchState === "component1" ? nameComponent1 : nameComponent2,
            }
          : {})}
      >
        {switchState === "component1" ? component1 : component2}
      </Card>
    </div>
  );
};
