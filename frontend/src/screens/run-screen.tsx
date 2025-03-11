import { Row, Container, Col } from "react-grid-system";
import { Navbar, PlotComponent, ListEditor, SwitchCard } from "./../components";
import { useNavigate } from "react-router-dom";
import { spacing } from "../theme";
import { styled } from "styled-components";
import {
  mockFormDataParameters,
  mockFormDataPlotSettings,
  mockPlotData,
  mockPlotLayout,
} from "./mockUpData";
import { InputValueType } from "../components/forms/form";
import React, { useState } from "react";

const StyledCardsRow = styled(Row)`
  margin-top: ${spacing("small")};
  height: 85vh;
  align: stretch;
`;

export const RunScreen: React.FC = () => {
  const navigate = useNavigate();


  const [plotData, setPlotData] = useState(mockPlotData);
  function onChangePlotSettings(data: Record<string, InputValueType>) {
    let new_colors: string | string[] = "purple";

  if (Array.isArray(data.colors)) {
    if (data.colors.length === 1) {
      new_colors = data.colors[0];
    } else if (data.colors.length > 1) {
      new_colors = data.colors;
    }
  }

    const plotType = data.type as "scatter" || "bar";

    const updatedMockPlotData: Partial<Plotly.Data>[] = [
      {
        ...mockPlotData[0] as Plotly.ScatterData,
        type: plotType,
        marker: { color: new_colors } ,
      },
    ];

    setPlotData(updatedMockPlotData);
  }

  const plotComponent = (
    <PlotComponent data={plotData} layout={mockPlotLayout} />
  );

  const listEditorComponent = (
    <ListEditor
      formDataParameters={mockFormDataParameters}
      onChangeParamters={() => {}}
      formDataPlotSettings={mockFormDataPlotSettings}
      onChangePlotSettings={onChangePlotSettings}
    />
  );

  return (
    <div>
      <Navbar
        allowRunEdit={true}
        title="New Run"
        onNavigateHome={() => navigate("/")}
        onOpenSettings={() => {}}
        onOpenHelp={() => {}}
      />
      <Container fluid style={{ margin: 0 }}>
        <StyledCardsRow>
          <Col md={"content"}>
            <SwitchCard
              nameComponent1="List"
              component1={listEditorComponent}
              nameComponent2="Node"
              component2={
                <p>
                  😲 Ohh you shouldn't come here - we're not finished yet.{" "}
                  <br />
                  Quickly click on the switch again. 👀
                </p>
              }
            />
          </Col>
          <Col>
            <SwitchCard
              nameComponent1="Plot"
              component1={plotComponent}
              nameComponent2="Table"
              component2={
                <p>
                  🚧 Construction is still going on here and there is absolutely
                  nothing to see 🚧
                </p>
              }
            />
          </Col>
        </StyledCardsRow>
      </Container>
    </div>
  );
};
