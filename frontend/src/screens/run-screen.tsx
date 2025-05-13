import React, { useCallback, useEffect, useState } from "react";
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
  footerMessages,
  mockPlots,
  mockTableData,
} from "./mockUpData";
import { DataTable } from "../components/data-table";
import { SelectedStep } from "../components/sidebar/types";
import { callApiWithParameters, emptyRunData } from "../utils";

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

const StyledTableContainer = styled.div`
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

  const randomMessage = footerMessages[Math.floor(Math.random() * footerMessages.length)];
  const runName = location.state?.runName;

  const [runData, setRunData] = useState(emptyRunData);
  const [plots, setPlots] = useState(mockPlots);
  const [tableData, setTableData] = useState(mockTableData);

  const handleStepSelection = (selectedStep: SelectedStep | undefined) => {
    if (selectedStep) {
      void callApiWithParameters("navigate_to_step/", {
        run_name: runName,
        section: selectedStep.section,
        index: String(selectedStep.index),
      }).then(() => {
        void getRunData();
        void getStepPlots();
        void getStepTable();
      });
    }
  };

  const getRunData = useCallback(async () => {
    const response = await callApiWithParameters("get_run_data/", {
      run_name: runName,
    });
    if (response) {
      setRunData(response.data);
    }
  }, [runName]);

  const getStepPlots = useCallback(async () => {
    const response = await callApiWithParameters("get_step_plots/", {
      run_name: runName,
    });
    if (response) {
      const data = response.data;

      let rawPlots = [];
      if (data.length > 0) {
        for (var plot of data){
          rawPlots.push(JSON.parse(plot));
        }
      }

      setPlots(rawPlots);
    }
  }, [runName]);

  const getStepTable = useCallback(async () => {
    const response = await callApiWithParameters("get_step_table/", {
      run_name: runName,
    });
    if (response) {
      const data = response.data;
      setTableData(data);
    }
  }, [runName]);

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([getRunData(), getStepPlots(), getStepTable()]);
    };

    void fetchData();
  }, [getRunData, getStepPlots, getStepTable]);

  const onFormSubmit = () => {
    void getRunData();
    void getStepPlots();
    void getStepTable();
  };

  const plotComponent = (
    <StyledPlotContainer>
      {plots.map((plot) => (
        <PlotComponent data={plot.data} layout={plot.layout}/>
      ))}
    </StyledPlotContainer>
  );

  const tableComponent = (
    <StyledTableContainer>
      <DataTable data={tableData} />
    </StyledTableContainer>
  );

  const listEditorComponent = (
    <ListEditor
      onFormSubmit={onFormSubmit}
      runName={runName}
      handleStepSelection={handleStepSelection}
      runData={runData}
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
              component2={tableComponent}
            />
          </StyledCol>
          <FooterText>{randomMessage}</FooterText>
        </StyledFlexColumn>
      </StyledCardRow>
    </div>
  );
};
