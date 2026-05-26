import { Navbar, NodeEditor, PlotDownloadSettings } from "@protzilla/app";
import {
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
  emptyRunData,
  footerMessages,
  Image,
  StepID,
  StepOutputInfo,
  SwitchComponent,
} from "@protzilla/utils";
import { Figure } from "plotly.js";
import React, { useCallback, useEffect, useState } from "react";
import { Col } from "react-grid-system";
import { useLocation, useNavigate } from "react-router-dom";
import { styled } from "styled-components";

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

  const runName = location.state?.runName;

  const [runData, setRunData] = useState(emptyRunData);
  const [plots, setPlots] = useState<Figure[]>();
  const [selectedPlot, setSelectedPlot] = useState<Figure>({ data: [], layout: {} });
  const [availableTables, setAvailableTables] = useState<StepOutputInfo[]>();

  // Static PNGs sent as base64
  const [images, setImages] = useState<Image[]>([]);
  const [availableImages, setAvailableImages] = useState<StepOutputInfo[]>([]);

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
        setPlots(undefined);
        setAvailableImages([]);

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
      for (const output of response.outputs) {
        if (output.output_type === "dataframe" || output.output_type === "list")
          tableOutputs.push(output);
        else if (output.output_type === "png_base64") imageOutputs.push(output);
      }
      setAvailableTables(tableOutputs);
      setAvailableImages(imageOutputs);
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

  useEffect(() => {
    const fetchImages = async () => {
      const imagePromises = availableImages.map(async (output_info) => {
        const response = await callApiWithParameters("get_png_from_step/", {
          run_name: runName,
          step_id: runData.current_step_id,
          output_key: output_info.label,
        });
        return {
          title: output_info.label,
          alt: output_info.label,
          data: "data:image/png;base64,".concat(response.data),
        };
      });

      try {
        const resolvedImages = await Promise.all(imagePromises);
        setImages(resolvedImages);
      } catch (error) {
        console.error("Failed to fetch image data:", error);
      }
    };

    if (availableImages.length > 0) {
      void fetchImages();
    } else {
      setImages([]);
    }
  }, [availableImages, runName, runData.current_step_id]);

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
