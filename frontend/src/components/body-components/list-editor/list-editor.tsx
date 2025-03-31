import React from "react";
import { styled } from "styled-components";

import { ListEditorProps } from "./list-editor.props";
import { color, spacing } from "../../../theme";
import { FlexRow } from "../../box";
import { Form } from "../../forms/form";
import { Sidebar } from "../../sidebar";

const StyledRow = styled(FlexRow)`
  gap: ${spacing("verySmall")};
  align-items: flex-start;
  height: 100%;
`;

const StyledDivider = styled.div`
  width: 1px;
  background-color: ${color("secondary")};
  flex-grow: 1;
  align-self: stretch;
  margin-right: ${spacing("small")};
`;

const StyledFormColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("large")};
  width: 20vw;
  min-width: 250px;
  max-width: 500px;
  padding-top: ${spacing("small")};
  margin: 0 ${spacing("small")};
`;

export const ListEditor: React.FC<ListEditorProps> = ({
  formDataParameters,
  onChangeParameters,
  formDataPlotSettings,
  onChangePlotSettings,
  runName,
  handleStepSelection
}) => {
  return (
    <StyledRow>
      <Sidebar runName={runName}
        handleStepSelection={handleStepSelection}
      />

      <StyledDivider />

      <StyledFormColumn>
        <Form formData={formDataParameters} onChange={onChangeParameters} />
        <Form formData={formDataPlotSettings} onChange={onChangePlotSettings} />
      </StyledFormColumn>
    </StyledRow>
  );
};
