import React, { useState } from "react";
import { styled } from "styled-components";

import { ContentCardProps } from "./content-card.props";
import { spacing } from "../../../theme";
import { Switch } from "../../switch";
import { Card } from "../../card";

const SwitchDiv = styled.div`
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding-bottom: ${spacing("small")};
`;

const StyledCard = styled(Card)`
  height: 100%;
`;

export const ContentCard: React.FC<ContentCardProps> = ({
  plotComponent,
  tableComponent = <p>Caution, construction is in progress here! Come back later</p>
}) => {
  const [switchState, setSwitchState] = useState<string>(
    "plot",
  );

  return (
    <div>
      <SwitchDiv>
        <Switch
          options={[
            { value: "plot", label: "Plot" },
            { value: "table", label: "Table"},
          ]}
          value={switchState}
          onChange={setSwitchState}
          defaultValue="plot"
          isDisabled={false}
        />
      </SwitchDiv>
      <StyledCard title={switchState === "plot" ? "Plot" : "Table"}>
        {switchState === "plot" ? plotComponent : tableComponent}
      </StyledCard>
    </div>
  );
};
