import { ListEditor, Navbar, NodeEditor, PlotDownloadSettings } from "@protzilla/app";
import {
  CSVButton,
  DataTable,
  FlexColumn,
  FlexRow,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  SwitchCard,
} from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import {
  callApiWithParameters,
  dummyTextComponent1,
  emptyRunData,
  footerMessages,
  StepIID,
  SwitchComponent,
  Table,
} from "@protzilla/utils";
import { Figure } from "plotly.js";
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
  min-height: 0;
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

const StyledContentContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: ${spacing("small")};
`;

const StyledContentDiv = styled.div`
  display: flex;
  flex-direction: column;
`;

const StyledCSVButton = styled(CSVButton)`
  width: auto;
  align-telf: flex-end;
  margin-top: ${spacing("buttonGap")};
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
  const [plots, setPlots] = useState<Figure[]>();
  const [selectedPlot, setSelectedPlot] = useState<Figure>({ data: [], layout: {} });
  const [tableData, setTableData] = useState<Table[]>();

  const [isDownloadModalOpen, openDownloadModal, closeDownloadModal] = useToggleableState(false);

  const navigateOrRefreshSteps = (stepIID?: StepIID) => {
    /*
      If a step is selected, navigate to that step.
      If no step is selected, just refresh the run data to update the run list.
    */

    if (stepIID) {
      void callApiWithParameters("navigate_to_step/", {
        run_name: runName,
        step_iid: stepIID,
      }).then(() => {
        void getRunData();
        void getStepPlots();
        void getStepTable(); // Bloat :c
      });
    } else {
      void getRunData();
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
  }, [runName]);

  const onFormSubmit = () => {
    void getRunData();
    void getStepPlots();
    void getStepTable();
  };

  const handleDownloadPlot = (plot: Figure) => {
    setSelectedPlot(plot);
    openDownloadModal();
  };

  let plotPlaceholderMessage;
  if (runData.current_step_has_plot) {
    plotPlaceholderMessage = "Run calculation to generate plot.";
  } else {
    plotPlaceholderMessage = "No plot available for this step.";
  }

  const plotComponent = (
    <StyledContentContainer>
      {plots && plots.length > 0 ? (
        <>
          {plots.map((plot, index) => (
            <StyledContentDiv key={index}>
              <PlotComponent data={plot.data} layout={plot.layout} hasResizing={true} />
              <SecondaryButton
                text="Download plot"
                style={{ width: "auto", alignSelf: "flex-start" }}
                onClick={() => {
                  handleDownloadPlot(plot);
                }}
              />
            </StyledContentDiv>
          ))}
          <PlotDownloadSettings
            isOpen={isDownloadModalOpen}
            onClose={closeDownloadModal}
            data={selectedPlot.data}
            layout={selectedPlot.layout}
          />
        </>
      ) : (
        <SectionTitle baseComponent={"h4"} description={plotPlaceholderMessage} />
      )}
    </StyledContentContainer>
  );

  const singleTableComponent = (table: Table) => (
    <StyledContentDiv>
      <DataTable data={table.table} />
      <StyledCSVButton data={table.table} fileName={table.name} />
    </StyledContentDiv>
  );

  const tableComponent = (
    <StyledContentContainer>
      {tableData && tableData.length > 0 ? (
        <SwitchCard
          hasShadow={false}
          components={tableData.map((table) => ({
            value: singleTableComponent(table),
            name: table.name,
          }))}
        />
      ) : (
        <SectionTitle
          baseComponent={"h4"}
          description={
            "No data table available for this step (yet). With large datasets it may take a while for tables to be displayed."
          }
        />
      )}
    </StyledContentContainer>
  );

  const otherComponent = (
    <SwitchCard hasShadow={false} components={[{ name: "🚧", value: dummyTextComponent1 }]} />
  );

  const nodeEditorComponent = (
    <NodeEditor
      onFormSubmit={onFormSubmit}
      runName={runName}
      navigateOrRefreshSteps={navigateOrRefreshSteps}
      runData={runData}
    />
  );

  const __list_editor_temp_component = (
    <StyledContentContainer>
      <SectionTitle
        baseComponent={"p"}
        description={"The List Editor is broken and needs to be refactored"}
      />
    </StyledContentContainer>
  )

  const listEditorComponent = (
    <ListEditor
      onFormSubmit={onFormSubmit}
      runName={runName}
      navigateOrRefreshSteps={navigateOrRefreshSteps}
      runData={runData}
    />
  );

  const editorModes = [
    { name: "List", value: __list_editor_temp_component },
    { name: "Node", value: nodeEditorComponent },
  ];

  // TODO: Replace this with appropriate data from runData
  // Else it resets whenever the run data is reset
  const selectedEditorMode: SwitchComponent["name"] = "Node";
  // const selectedEditorMode = runData.editor_mode;

  const selectEditorMode = (mode: SwitchComponent) => {
    console.log("Changed to", mode.name);
    // TODO: This API call has not been implemented yet
    // void callApiWithParameters("set_editor_mode/", {
    //   run_name: runName,
    //   mode: mode.name
    // }).then(() => {
    //   void getRunData();
    //   void getStepPlots();
    //   void getStepTable();
    // });
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      <StyledNavbar
        showRunInformation={true}
        title={runName}
        memoryUsage={runData.memory_usage}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => void navigate("/")}
      />

      <StyledCardRow>
        <StyledFlexColumn>
          <StyledListSwitchCard
            components={editorModes}
            selection={selectedEditorMode}
            callback={selectEditorMode}
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
              styleProps={{ height: "calc(100% - 3em)" }}
              components={[
                { name: "Plots", value: plotComponent },
                { name: "Tables", value: tableComponent },
                { name: "Other Output", value: otherComponent },
              ]}
              hasCardTitle={false}
            />
          </StyledCol>
          <FooterText>{randomMessage}</FooterText>
        </StyledFlexColumn>
      </StyledCardRow>
    </div>
  );
};
