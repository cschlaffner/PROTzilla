import React, { useEffect, useState } from "react";
import { Col, Container, Row } from "react-grid-system";
import { useLocation, useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { spacing } from "../theme";
import { ListEditor, Navbar, PlotComponent, PlotProps, SwitchCard } from "./../components";
import {
  dummyTextComponent1,
  dummyTextComponent2,
  footerMessages,
  mockFormDataParameters,
  mockFormDataPlotSettings,
  mockPlotData,
  mockPlotLayout,
} from "./mockUpData";
import { InputValueType } from "../components/forms/form";
import { callApiWithParameters } from "../utils";

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;
const StyledCardsRow = styled(Row)`
  margin-top: ${spacing("small")};
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

const FooterText = styled.div`
  text-align: center;
  padding: ${spacing("small")};
  font-size: 14px;
  color: gray;
  position: absolute;
  width: 100%;
  bottom: 0;
`;

export const RunScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const randomMessage =
    footerMessages[Math.floor(Math.random() * footerMessages.length)];

  const [runName] = useState<string>(location.state?.existingRun);
  const [plotData, setPlotData] = useState(mockPlotData);
  const [plotLayout, setPlotLayout] = useState(mockPlotLayout);
  function onChangePlotSettings(data: Record<string, InputValueType>) {
    let newColors: string | string[] = "purple";

    if (Array.isArray(data.colors)) {
      if (data.colors.length === 1) {
        newColors = data.colors[0];
      } else if (data.colors.length > 1) {
        newColors = data.colors;
      }
    }

    const plotType = data.type as "scatter";

    const updatedMockPlotData: Partial<Plotly.Data>[] = [
      {
        ...(mockPlotData[0] as Plotly.ScatterData),
        type: plotType,
        marker: { color: newColors },
      },
    ];

    setPlotData(updatedMockPlotData);
  }

  useEffect(() => {
    const fetchData = async () => {
      const data = await callApiWithParameters("get_step_plots/", {run_name: runName});
      if (data) {
        const { data: rawData, layout: rawLayout } = data;
        console.log(data);
        const parsedData = parsePlotlyJson(rawData);
        const parsedLayout = parsePlotlyJson(rawLayout);
        setPlotData(parsedData);
        setPlotLayout(parsedLayout);
        console.log("Gute Daten", parsedData);
        console.log("Viele Daten", parsedLayout);
      }
    };
    void fetchData();
  }, []);

  const parsePlotlyJson = (input: any) => {
    if (typeof input === "string") {
      try {
        const parsed = JSON.parse(input);
  
        // If it's an array, parse its elements if needed
        if (Array.isArray(parsed)) {
          return parsed.map((item) => (typeof item === "string" ? JSON.parse(item) : item));
        }
        return parsed;
      } catch (error) {
        console.error("JSON parsing error:", error);
        return input; // Return as-is if parsing fails
      }
    }
    return input; // If already an object, return as-is
  };

  const plotComponent = (
    <StyledPlotContainer>
      <PlotComponent data={plotData} layout={plotLayout} />
    </StyledPlotContainer>
  );

  const listEditorComponent = (
    <ListEditor
      formDataParameters={mockFormDataParameters}
      onChangeParamters={() => {}}
      formDataPlotSettings={mockFormDataPlotSettings}
      onChangePlotSettings={onChangePlotSettings}
      runName={runName}
    />
  );

  return (
    <div>
      <StyledNavbar
        allowRunEdit={true}
        title={runName}
        onNavigateHome={() => navigate("/")}
        onOpenSettings={() => {}}
        onOpenHelp={() => {}}
      />

      <Container fluid>
        <StyledCardsRow>
          <StyledCol md={"content"} style={{ paddingRight: 0 }}>
            <SwitchCard
              nameComponent1="List"
              component1={listEditorComponent}
              nameComponent2="Node"
              component2={dummyTextComponent1}
              hasCardTitle={false}
            />
          </StyledCol>
          <StyledCol>
            <SwitchCard
              nameComponent1="Plot"
              component1={plotComponent}
              nameComponent2="Table"
              component2={dummyTextComponent2}
            />
          </StyledCol>
        </StyledCardsRow>
      </Container>
      <FooterText dangerouslySetInnerHTML={{ __html: randomMessage }} />
    </div>
  );
};
