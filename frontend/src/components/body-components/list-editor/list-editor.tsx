import React, { useState } from "react";
import { styled } from "styled-components";

import { FlexColumn, FlexRow } from "../../box";
import { Form } from "../../forms/form";
import { ListEditorProps } from "./list-editor.props";
import { spacing } from "../../../theme";


const StyledFlexRow = styled(FlexRow)`
    gap: ${spacing("small")};
`;

const StyledFormColumn = styled(FlexColumn)`
    gap: ${spacing("large")};
`;

export const ListEditor: React.FC<ListEditorProps> = ({
  formDataParameters,
  onChangeParamters,
  formDataPlotSettings,
  onChangePlotSettings,
}) => {

  return (
    <StyledFlexRow>
        <p>Sidebar</p>
        <StyledFormColumn>
            <Form formData={formDataParameters} onChange={onChangeParamters} />
            <Form formData={formDataPlotSettings} onChange={onChangePlotSettings} />
        </StyledFormColumn>
    </StyledFlexRow>
  );
};
