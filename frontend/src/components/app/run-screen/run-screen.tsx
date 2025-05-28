import { ListEditor, Navbar } from "@protzilla/app";
import {
  DataTable,
  FlexColumn,
  FlexRow,
  PlotComponent,
  SectionTitle,
  SwitchCard,
} from "@protzilla/core";
import { spacing } from "@protzilla/theme";
import {
  callApiWithParameters,
  dummyTextComponent1,
  emptyRunData,
  footerMessages,
  mockPlots,
  mockTableData,
  SelectedStep,
} from "@protzilla/utils";
import React, { useCallback, useEffect, useState } from "react";
import { Col } from "react-grid-system";
import { useLocation, useNavigate } from "react-router-dom";
import { styled } from "styled-components";

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
  flex-direction: column;
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

      const rawPlots = [];
      if (data.length > 0) {
        for (const plot of data) {
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
      {plots.length > 0 ? (
        plots.map((plot, index) => (
          <PlotComponent key={index} data={plot.data} layout={plot.layout} hasResizing={true} />
        ))
      ) : (
        <SectionTitle baseComponent={"h4"} description={"No plot available for this step."} />
      )}
    </StyledPlotContainer>
  );

  const tableComponent = (
    <StyledTableContainer>
      {tableData.length > 0 ? (
        <DataTable data={tableData} />
      ) : (
        <SectionTitle baseComponent={"h4"} description={"No data table available for this step."} />
      )}
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
