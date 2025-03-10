import React, { useState } from "react";
import { styled } from "styled-components";

import { EditorCardProps } from "./editor-card.props";
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

export const EditorCard: React.FC<EditorCardProps> = ({
  listEditorComponent,
  nodeEditorComponent = <p>Caution, construction is in progress here! Come back later</p>
}) => {
  const [switchState, setSwitchState] = useState<string>(
    "list",
  );

  return (
    <div>
      <SwitchDiv>
        <Switch
          options={[
            { value: "list", label: "List" },
            { value: "node", label: "Node"},
          ]}
          value={switchState}
          onChange={setSwitchState}
          defaultValue="plot"
          isDisabled={false}
        />
      </SwitchDiv>
      <StyledCard title={switchState === "list" ? "List" : "Node"}>
        {switchState === "list" ? listEditorComponent : nodeEditorComponent}
      </StyledCard>
    </div>
  );
};
