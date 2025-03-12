// @ts-expect-error - required for ploty resizing
import Plotly from "plotly.js-dist-min";
import React, { useState } from "react";
import { styled } from "styled-components";
import { Sidebar } from "../../sidebar";
import { ListEditorProps } from "./list-editor.props";
import { spacing } from "../../../theme";
import { Form } from "../../forms/form";
import { Icon } from "../../icon";
import { FlexRow } from "../../box";

const StyledRow = styled(FlexRow)`
  gap: ${spacing("medium")};
  align-items: flex-start;
`;

const StyledFormColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("large")};
  width: 20vw;
  min-width: 250px;
  max-width: 500px;
`;

const SidebarHeader = styled.div<{ isCollapsed: boolean }>`
  display: flex;
  justify-content: ${({ isCollapsed }) => (isCollapsed ? "left" : "flex-end")};
  width: auto;
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


  // const handleClick = () => {
  //   setIsCollapsed((prev) => !prev);
  //   const plotElement = document.querySelector(".js-plotly-plot");
  //   if (plotElement instanceof HTMLElement) {
  //     Plotly.Plots.resize(plotElement);
  //   }
  // };

  return (
    <StyledRow>
      <Sidebar/>
      <StyledFormColumn>
        <Form formData={formDataParameters} onChange={onChangeParamters} />
        <Form formData={formDataPlotSettings} onChange={onChangePlotSettings} />
      </StyledFormColumn>
    </StyledRow>
  );
};
