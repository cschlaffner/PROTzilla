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
  flex-grow: 1;
`;

export const ContentCard: React.FC<ContentCardProps> = ({
  plotComponent,
  tableComponent = <p>Caution, construction is in progress here! Come back later</p>
}) => {
  const [listNodeSwitch, setListNodeSwitch] = useState<string>(
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
          value={listNodeSwitch}
          onChange={setListNodeSwitch}
          defaultValue="plot"
          isDisabled={false}
        />
      </SwitchDiv>
      <StyledCard title={listNodeSwitch === "plot" ? "Plot" : "Table"}>
        {listNodeSwitch === "plot" ? plotComponent : tableComponent}
      </StyledCard>
    </div>
  );
};
