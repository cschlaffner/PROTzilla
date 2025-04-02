import React, { useEffect, useState } from "react";
import { Col } from "react-grid-system";
import { useLocation, useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { spacing } from "../theme";
import {
  FlexColumn,
  FlexRow,
  ListEditor,
  Navbar,
  PlotComponent,
  SwitchCard,
} from "./../components";
import {
  dummyTextComponent1,
  dummyTextComponent2,
  footerMessages,
  mockFormDataParameters,
  mockPlotData,
  mockPlotLayout,
} from "./mockUpData";
import { SelectedStep } from "../components/sidebar/types";
import { callApiWithParameters } from "../utils";
import { InputValueType } from "../components/forms/form";

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;
const StyledCardRow = styled(FlexRow)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  flex: 1;
  height: 100%;
`;

const StyledFlexColumn = styled(FlexColumn)`
  height: 100%;
`;

const StyledCol = styled(Col)`
  display: flex;
  flex-direction: column;
  min-width: 0;
`;

const StyledListSwitchCard = styled(SwitchCard)`
  height: 100%;
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
  width: 100%;
`;

export const RunScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const randomMessage =
    footerMessages[Math.floor(Math.random() * footerMessages.length)];
  const [runName] = useState<string>(location.state?.existingRun);
  const [formData, setFormData] = useState(mockFormDataParameters);
  const [plotData, setPlotData] = useState(mockPlotData);
  const [plotLayout, setPlotLayout] = useState(mockPlotLayout);
  const [userInput, setUserInput] = useState<Record<string, InputValueType>>({});

  const handleStepSelection = (selectedStep: SelectedStep | null) => {
    if (selectedStep) {
      void callApiWithParameters("navigate_to_step/", {
        run_name: runName,
        section: selectedStep.section,
        index: String(selectedStep.index),
      })
        .then(() => {
          return getStepForm({});
        })
        .then(() => {
          return getStepPlots();
        });
    }
  };

  const onChangeParameters = (data: Record<string, InputValueType>) => {
    setUserInput(data);
  }

  const getStepPlots = async () => {
    const response = await callApiWithParameters("get_step_plots/", {
      run_name: runName,
    });
    if (response) {
      const data = response.data;

      let rawData = [];
      let rawLayout = [];
      if (data.length > 0) {
        const paredData = JSON.parse(data[0]);
        rawData = paredData.data;
        rawLayout = paredData.layout;
      }

      setPlotData(rawData);
      setPlotLayout(rawLayout);
    }
  };

  const getStepForm = async (userInput: Record<string, InputValueType>) => {
    const response = await callApiWithParameters("get_step_form/", {
      run_name: runName,
      data: userInput,
    });
    if (response) {
      const data = response.data;

      setFormData(data);
    }
  };
  useEffect(() => {
    console.log(formData);
  }, [formData]);

  const calculateStep = async () => {
    await callApiWithParameters("calculate_step/", {
      run_name: runName,
      data: userInput,
    });
  };

  const plotComponent = (
    <StyledPlotContainer>
      <PlotComponent data={plotData} layout={plotLayout} />
    </StyledPlotContainer>
  );

  const listEditorComponent = (
    <ListEditor
      formDataParameters={formData}
      onChangeParameters={onChangeParameters}
      runName={runName}
      handleStepSelection={handleStepSelection}
      onCalculateStep={calculateStep}
    />
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <StyledNavbar
        allowRunEdit={true}
        title={runName}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => void navigate("/")}
      />

      <StyledCardRow>
        <StyledFlexColumn>
          <StyledListSwitchCard
            nameComponent1="List"
            component1={listEditorComponent}
            nameComponent2="Node"
            component2={dummyTextComponent1}
            hasCardTitle={false}
            styleProps={{
              display: "flex",
              flexDirection: "column",
              height: "100%",
            }}
          />
        </StyledFlexColumn>
        <StyledFlexColumn style={{ flex: 1 }}>
          <StyledCol>
            <SwitchCard
              nameComponent1="Plot"
              component1={plotComponent}
              nameComponent2="Table"
              component2={dummyTextComponent2}
            />
          </StyledCol>
          <FooterText>{randomMessage}</FooterText>
        </StyledFlexColumn>
      </StyledCardRow>
    </div>
  );
};
