import React, { useState } from "react";
import { styled } from "styled-components";
import { Form } from "../../forms/form";
import { ListEditorProps } from "./list-editor.props";
import { spacing } from "../../../theme";
import { Icon } from "../../icon";
import { Col, Row } from "react-grid-system";


const StyledRow = styled(Row)`
  gap: ${spacing("small")};
`;

const StyledFormColumn = styled(Col)`
  display: flex;
  flex-direction: column;
  gap: ${spacing("large")};
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

  const [isCollapsed, setIsCollapsed] = useState(false)

  const handleClick = () => {
    setIsCollapsed((prev) => !prev)
  }

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
