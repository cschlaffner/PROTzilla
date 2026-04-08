import { Navbar, NodeEditor, PlotDownloadSettings } from "@protzilla/app";
import {
  CSVButton,
  DataTable,
  FlexColumn,
  FlexRow,
  MolstarViewer,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  SwitchCard,
} from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import {
  ApiResponse,
  callApiWithParameters,
  Download,
  emptyRunData,
  footerMessages,
  Image,
  StepID,
  StepOutputInfo,
  SwitchComponent,
  Visualization,
} from "@protzilla/utils";
import { Figure } from "plotly.js";
import React, { useCallback, useEffect, useState } from "react";
import { Col } from "react-grid-system";
import { useLocation, useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { CrosslinkerInformation } from "../../core/shared/molstar-viewer/crosslinker-processing";
import { H3 } from "../../core/shared/text";

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
  align-self: flex-end;
  margin-top: ${spacing("buttonGap")};
`;

const FooterText = styled.div`
  text-align: center;
  padding: ${spacing("small")};
  font-size: 14px;
  color: gray;
  width: 100%;
`;

interface UseStepOutputsParams<TOutput, TResponse, TResult> {
  available_outputs: TOutput[];
  endpoint: string;
  runName: string;
  stepId?: string;
  transform: (output: TOutput, response: TResponse) => TResult;
}

function useCertainStepOutputs<TOutput extends StepOutputInfo, TResponse, TResult>({
  available_outputs,
  endpoint,
  runName,
  stepId,
  transform,
}: UseStepOutputsParams<TOutput, TResponse, TResult>): TResult[] {
  const [data, setData] = useState<TResult[]>([]);

  useEffect(() => {
    if (!stepId || available_outputs.length === 0) {
      setData([]);
      return;
    }

    const fetchData = async () => {
      try {
        const responses = await Promise.all(
          available_outputs.map(async (output) => {
            const response: TResponse = await callApiWithParameters(endpoint, {
              run_name: runName,
              step_id: stepId,
              output_key: output.label,
            });

            return transform(output, response);
          }),
        );

        setData(responses);
      } catch (error) {
        console.error("Failed to fetch outputs:", error);
      }
    };

    void fetchData();
  }, [available_outputs, endpoint, runName, stepId, transform]);

  return data;
}

export const RunScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const runName = location.state?.runName;

  const [runData, setRunData] = useState(emptyRunData);
  const [plots, setPlots] = useState<Figure[]>();
  const [selectedPlot, setSelectedPlot] = useState<Figure>({ data: [], layout: {} });
  const [availableTables, setAvailableTables] = useState<StepOutputInfo[]>();

  const [availableVisualizations, setAvailableVisualizations] = useState<StepOutputInfo[]>([]);
  const transformVisualization = useCallback(
    (_output: StepOutputInfo, response: ApiResponse<Visualization>) => ({
      proteinEntryId: response.data.proteinEntryId,
      cifString: response.data.cifString,
      crosslinks: response.data.crosslinks,
    }),
    [],
  );
  const visualizations = useCertainStepOutputs<
    StepOutputInfo,
    ApiResponse<Visualization>,
    { proteinEntryId: string; cifString: string; crosslinks?: CrosslinkerInformation[] }
  >({
    available_outputs: availableVisualizations,
    endpoint: "get_step_visualizations/",
    runName: runName,
    stepId: runData.current_step_id,
    transform: transformVisualization,
  });

  const [availableDownloads, setAvailableDownloads] = useState<StepOutputInfo[]>([]);
  const transformDownload = useCallback(
    (output: StepOutputInfo, response: ApiResponse<Download>) => ({
      title: output.label,
      data: response.data.data,
    }),
    [],
  );
  const downloads = useCertainStepOutputs<
    StepOutputInfo,
    ApiResponse<Download>,
    { title: string; data: Record<string, unknown> }
  >({
    available_outputs: availableDownloads,
    endpoint: "get_downloads_from_step/",
    runName: runName,
    stepId: runData.current_step_id,
    transform: transformDownload,
  });

  // Static PNGs sent as base64
  const [availableImages, setAvailableImages] = useState<StepOutputInfo[]>([]);
  const transformImage = useCallback(
    (output: StepOutputInfo, response: ApiResponse<Image>) => ({
      title: output.label,
      alt: output.label,
      data: "data:image/png;base64," + response.data.data,
    }),
    [],
  );
  const images = useCertainStepOutputs<
    StepOutputInfo,
    ApiResponse<Image>,
    { title: string; alt: string; data: string }
  >({
    available_outputs: availableImages,
    endpoint: "get_png_from_step/",
    runName: runName,
    stepId: runData.current_step_id,
    transform: transformImage,
  });

  const [isDownloadModalOpen, openDownloadModal, closeDownloadModal] = useToggleableState(false);

  const getFooterMessage = () => {
    const currentTimestamp = new Date();
    const currentHour =
      String(currentTimestamp.getFullYear()) +
      "-" +
      String(currentTimestamp.getMonth() + 1) +
      "-" +
      String(currentTimestamp.getDate()) +
      "-" +
      String(currentTimestamp.getHours());

    const storedHour = localStorage.getItem("footerMessageHour");
    const storedMessage = localStorage.getItem("footerMessage") ?? "";

    if (storedHour == currentHour) {
      return storedMessage;
    } else {
      const newMessage = footerMessages[Math.floor(Math.random() * footerMessages.length)];
      localStorage.setItem("footerMessage", newMessage);
      localStorage.setItem("footerMessageHour", currentHour);
      return newMessage;
    }
  };

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
        setAvailableTables(undefined);
        setAvailableDownloads([]);
        setPlots(undefined);
        setAvailableImages([]);
        setAvailableVisualizations([]);

        void getRunData();
        void getStepPlots();
        void getCurrentStepOutputLabels();
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

  const getCurrentStepOutputLabels = useCallback(async () => {
    const response = await callApiWithParameters("get_current_step_output_labels/", {
      run_name: runName,
    });
    if (response) {
      const tableOutputs = [];
      const imageOutputs = [];
      const downloadOutputs = [];
      const visualizationOutputs = [];
      for (const output of response.outputs) {
        if (output.output_type === "dataframe" || output.output_type === "list")
          tableOutputs.push(output);
        else if (output.output_type === "png_base64") imageOutputs.push(output);
        else if (output.output_type === "download") downloadOutputs.push(output);
        else if (output.output_type === "visualization") visualizationOutputs.push(output);
      }
      setAvailableTables(tableOutputs);
      setAvailableImages(imageOutputs);
      setAvailableDownloads(downloadOutputs);
      setAvailableVisualizations(visualizationOutputs);
    }
  }, [runName]);

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([getRunData(), getStepPlots(), getCurrentStepOutputLabels()]);
    };

    void fetchData();
  }, [getRunData, getStepPlots, getCurrentStepOutputLabels]);

  const onFormSubmit = () => {
    setAvailableTables(undefined);
    setAvailableImages([]);
    setPlots(undefined);
    setAvailableDownloads([]);
    setAvailableVisualizations([]);
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

  const visualizationComponent = (
    <StyledContentContainer>
      {visualizations.length > 0 ? (
        visualizations.map((viz) => (
          <StyledContentDiv key={viz.proteinEntryId}>
            <MolstarViewer cifText={viz.cifString} crosslinks={viz.crosslinks} />
          </StyledContentDiv>
        ))
      ) : (
        <SectionTitle baseComponent="h4" description="Structure-visualization is loading..." />
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
        <SectionTitle baseComponent={"h4"} description={"Output-tables are loading..."} />
      )}
    </StyledContentContainer>
  );

  const imageComponent = (
    <StyledContentContainer>
      {images.length > 0 ? (
        <>
          {images.map((image) => {
            return (
              <>
                <H3>{image.title}</H3>
                <img src={image.data} alt={image.alt} />
              </>
            );
          })}
        </>
      ) : (
        <SectionTitle baseComponent={"h4"} description={"No images"} />
      )}
    </StyledContentContainer>
  );

  const downloadJson = (filename: string, content: string) => {
    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();

    URL.revokeObjectURL(url);
  };

  const downloadComponent = (
    <StyledContentContainer>
      {downloads.length > 0 ? (
        downloads.flatMap((download) =>
          Object.entries(download.data).map(([filename, content]) => (
            <SecondaryButton
              key={`${download.title}-${filename}`}
              text={filename}
              style={{ width: "fit-content" }}
              onClick={() => {
                downloadJson(filename, JSON.stringify(content, null, 2));
              }}
            />
          )),
        )
      ) : (
        <SectionTitle baseComponent={"h4"} description={"Available downloads are loading..."} />
      )}
    </StyledContentContainer>
  );

  const nodeEditorComponent = (
    <NodeEditor
      onFormSubmit={onFormSubmit}
      runName={runName}
      navigateOrRefreshSteps={navigateOrRefreshSteps}
      runData={runData}
    />
  );

  const editorModes = [{ name: "Flow", value: nodeEditorComponent }];

  const selectedEditorMode: SwitchComponent["name"] = "Flow";

  const components = [
    plots && plots.length > 0 && { name: "Plots", value: plotComponent },
    availableTables && availableTables.length > 0 && { name: "Tables", value: tableComponent },
    availableImages.length > 0 && { name: "Images", value: imageComponent },
    availableDownloads.length > 0 && { name: "Downloads", value: downloadComponent },
    availableVisualizations.length > 0 && { name: "Visualizations", value: visualizationComponent },
  ].filter(Boolean) as { name: string; value: React.ReactNode }[];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      <StyledNavbar
        showRunInformation={true}
        title={runName}
        memoryUsage={runData.memory_usage}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => window.open("https://github.com/cschlaffner/PROTzilla/wiki/User-Guide")}
      />

      <StyledCardRow>
        <StyledFlexColumn>
          <StyledListSwitchCard
            components={editorModes}
            selection={selectedEditorMode}
            hasCardTitle={false}
            styleProps={{
              display: "flex",
              flexDirection: "column",
              height: "100%",
            }}
          />
        </StyledFlexColumn>
        <StyledFlexColumn style={{ flex: 1 }}>
          {components.length ? (
            <StyledCol>
              <SwitchCard
                key={runData.current_step_id}
                styleProps={{ height: "calc(100% - 3em)" }}
                components={components}
                hasCardTitle={false}
              />
            </StyledCol>
          ) : (
            <div style={{ flex: 1 }} />
          )}
          <FooterText>{getFooterMessage()}</FooterText>
        </StyledFlexColumn>
      </StyledCardRow>
    </div>
  );
};
