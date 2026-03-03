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
  StepID,
  SwitchComponent,
  Table,
  SelectedStep,
  StepOutputInfo,
} from "@protzilla/utils";
import { Figure } from "plotly.js";
import React, { useCallback, useEffect, useRef, useState } from "react";
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
  const [availableTables, setAvailableTables] = useState<StepOutputInfo[]>();

  const [isDownloadModalOpen, openDownloadModal, closeDownloadModal] = useToggleableState(false);
  const runDataRequestID = useRef(0);

  const navigateOrRefreshSteps = (stepID?: StepID) => {
    /*
      If a step is selected, navigate to that step.
      If no step is selected, just refresh the run data to update the run list.
    */

    if (stepID) {
      void callApiWithParameters("navigate_to_step/", {
        run_name: runName,
        step_id: stepID,
      }).then(() => {
        void getRunData();
        void getStepPlots();
        void getCurrentStepOutputLabels();
      });
    } else {
      void getRunData();
    }
  };

  const getRunData = useCallback(async () => {
    const requestId = (runDataRequestID.current += 1);
    const response = await callApiWithParameters("get_run_data/", {
      run_name: runName,
    });
    if (response) {
      if (requestId === runDataRequestID.current) {
        setRunData(response.data);
      }
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

  const getCurrentStepOutputLabels = useCallback(async () => {
    const response = await callApiWithParameters("get_current_step_output_labels/", {
      run_name: runName,
    });
    if (response) {
      const data = response.outputs;
      setAvailableTables(data);
    }
  }, [runName]);

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([getRunData(), getStepPlots(), getCurrentStepOutputLabels()]);
    };

    void fetchData();
  }, [getRunData, getStepPlots, getCurrentStepOutputLabels]);

  const onFormSubmit = () => {
    void getRunData();
    void getStepPlots();
    void getCurrentStepOutputLabels();
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

  const singleTableComponent = (tableLabel: string) => (
    <StyledContentDiv>
      <DataTable runName={runName} tableLabel={tableLabel} />
      <StyledCSVButton runName={runName} tableLabel={tableLabel} fileName={tableLabel} />
    </StyledContentDiv>
  );

  const tableComponent = (
    <StyledContentContainer>
      {availableTables && availableTables.length > 0 ? (
        <SwitchCard
          hasShadow={false}
          components={availableTables.map((output_info) => ({
            value: singleTableComponent(output_info.label),
            name: output_info.display_name,
          }))}
        />
      ) : (
        <SectionTitle
          baseComponent={"h4"}
          description={"This step does not provide any tables as output."}
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

  // const listEditorComponent = (
  //   <ListEditor
  //     onFormSubmit={onFormSubmit}
  //     runName={runName}
  //     navigateOrRefreshSteps={navigateOrRefreshSteps}
  //     runData={runData}
  //   />
  // );

  const editorModes = [
    // { name: "List", value: listEditorComponent },
    { name: "Flow", value: nodeEditorComponent },
  ];

  // TODO: Replace this with appropriate data from runData
  // Else it resets whenever the run data is reset
  const selectedEditorMode: SwitchComponent["name"] = "Flow";
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
