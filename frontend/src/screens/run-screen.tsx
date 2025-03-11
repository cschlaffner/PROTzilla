import { Row, Container, Col } from "react-grid-system";
import { Navbar, PlotComponent, ListEditor, SwitchCard } from "./../components";
import { useNavigate } from "react-router-dom";
import { spacing } from "../theme";
import { styled } from "styled-components";
import { mockFormDataParameters, mockFormDataPlotSettings, mockPlotData, mockPlotLayout } from "./mockUpData";
import { InputValueType } from "../components/forms/form";
import React, { useState } from "react";

const StyledCardsRow = styled(Row)`
  margin-top: ${spacing("small")};
  height: 85vh;
  display: flex;
  flex-wrap: nowrap;
`;

const StyledCol = styled(Col)`
  display: flex;
  flex-direction: column;
  min-width: 0; 
`;

const StyledPlotContainer = styled.div`
  width: 100%;
  height: 100%;
  display: flex;

`;

export const RunScreen: React.FC = () => {
  const navigate = useNavigate();

  const [plotLayout, setPlotLayout] = useState(mockPlotLayout);
  const [plotKey, setPlotKey] = useState(0);

  function onChangePlotSettings(data: Record<string, InputValueType>) {
    setPlotLayout((prevLayout) => ({ ...prevLayout, ...data }));
    setPlotKey((prevKey) => prevKey + 1); 
    console.log(plotLayout);
  }

  const plotComponent = (
    <StyledPlotContainer key={plotKey}> {/* WICHTIG: Key ans übergeordnete Element hängen */}
      <PlotComponent data={mockPlotData} layout={plotLayout} />
    </StyledPlotContainer>
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
      <Container fluid style={{ margin: 0}}>
        <StyledCardsRow>
          <StyledCol md={"content"}>
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
          </StyledCol>
          <StyledCol>
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
          </StyledCol>
        </StyledCardsRow>
      </Container>
    </div>
  );
};
