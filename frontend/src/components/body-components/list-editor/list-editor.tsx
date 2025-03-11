// @ts-expect-error - required for ploty resizing
import Plotly from "plotly.js-dist-min";
import React, { useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled } from "styled-components";

import { ListEditorProps } from "./list-editor.props";
import { spacing } from "../../../theme";
import { Form } from "../../forms/form";
import { Icon } from "../../icon";

const StyledRow = styled(Row)`
  gap: ${spacing("small")};
`;

const StyledFormColumn = styled(Col)`
  display: flex;
  flex-direction: column;
  gap: ${spacing("large")};
  min-width: 300px;
`;

const SidebarHeader = styled.div<{ isCollapsed: boolean }>`
  display: flex;
  justify-content: ${({ isCollapsed }) => (isCollapsed ? "left" : "flex-end")};
  width: ${({ isCollapsed }) => (isCollapsed ? "50px" : "250px")};
  padding: 5px;
  margin: 5px;
  cursor: pointer;
`;

export const ListEditor: React.FC<ListEditorProps> = ({
  formDataParameters,
  onChangeParamters,
  formDataPlotSettings,
  onChangePlotSettings,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleClick = () => {
    setIsCollapsed((prev) => !prev);
    const plotElement = document.querySelector(".js-plotly-plot");
    if (plotElement instanceof HTMLElement) {
      Plotly.Plots.resize(plotElement);
    }
  };

  return (
    <StyledRow>
      <SidebarHeader isCollapsed={isCollapsed}>
        <Icon
          icon={isCollapsed ? "chevronRight" : "chevronLeft"}
          onClick={handleClick}
        />
      </SidebarHeader>
      <StyledFormColumn>
        <Form formData={formDataParameters} onChange={onChangeParamters} />
        <Form formData={formDataPlotSettings} onChange={onChangePlotSettings} />
      </StyledFormColumn>
    </StyledRow>
  );
};
