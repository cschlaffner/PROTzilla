import React, { useState } from "react";
import { styled } from "styled-components";

import { SwitchCardProps } from "./switch-card.props";
import { spacing } from "../../../theme";
import { Switch } from "../../switch";
import { Card } from "../card";

const SwitchDiv = styled.div`
  display: flex;
  justify-content: flex-end;
  padding-bottom: ${spacing("small")};
`;

const StyledCard = styled(Card)`
  height: auto;
  width: auto;
`;

export const SwitchCard: React.FC<SwitchCardProps> = ({
  nameComponent1,
  component1,
  nameComponent2,
  component2,
}) => {
  const [switchState, setSwitchState] = useState<string>(
    "component1",
  );

  return (
    <div>
      <SwitchDiv>
        <Switch
          options={[
            { value: "component1", label: nameComponent1 },
            { value: "component2", label: nameComponent2 },
          ]}
          value={switchState}
          onChange={setSwitchState}
          defaultValue="component1"
          isDisabled={false}
        />
      </SwitchDiv>
      <StyledCard title={switchState === "component1" ? nameComponent1 : nameComponent2}>
        {switchState === "component1" ? component1 : component2}
      </StyledCard>
    </div>
  );
};
