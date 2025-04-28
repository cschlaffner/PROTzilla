import { Figure, Layout, PlotData } from "plotly.js";
import { useEffect, useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled } from "styled-components";

import { PlotDownloadSettingsProps } from "./plot-download-settings.props";
import {
  Button,
  Modal,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  TextInputField,
} from "../..";
import {
  CustomFontField,
  FileFormatField,
  FontField,
  HeightField,
  TextSizeField,
  TitleSizeField,
  WidthField,
} from "./plot-settings-input-fields";
import { usePlotSettings } from "./usePlotSettings";
import { border, borderColors, color, spacing } from "../../../theme";

const StyledModal = styled(Modal)`
  width: fit-content;
  max-width: 100%;
  height: fit-content;
  max-height: 100vh;
`;

const SettingsDiv = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

const PlotDiv = styled.div`
  width: fit-content;
  height: fit-content;
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  padding: 2px;
`;

const Footer = styled.div`
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: ${color("background")};
  display: flex;
  justify-content: flex-end;
  gap: ${spacing("smallButtonGap")};
  padding: ${spacing("smallButtonGap")};
  z-index: 10;
`;

export const PlotDownloadSettings: React.FC<PlotDownloadSettingsProps> = ({
  isOpen,
  onClose,
}) => {
  const {
    settings,
    loadSettings,
    saveSettings,
    computeDisplaySizes,
    setComputedSettings,
    downloadPlot,
    handleFileFormatChange,
    handleWidthChange,
    handleHeightChange,
    handleFontChange,
    handleCustomFontChange,
    handleTitleSizeChange,
    handleTextSizeChange,
    handleTitleChange,
  } = usePlotSettings(isOpen);

  const initialPlot = {
    data: [
      {
        marker: { color: "#4A536A" },
        x: ["Example 1"],
        y: [0.7],
        name: "Example 1",
        type: "bar",
      },
      {
        marker: { color: "#CE5A5A" },
        x: ["Example 2"],
        y: [0.3],
        name: "Example 2",
        type: "bar",
      },
    ],
    layout: {
      width: 400,
      height: 250,
      title: {
        font: { family: "Sans Serif", size: 15 },
        text: "Very important title",
      },
      xaxis: { anchor: "y", title: { text: "x-axis" } },
      yaxis: { anchor: "x", title: { text: "y-axis" } },
      template: {
        layout: {
          colorway: ["#4A536A", "#CE5A5A"],
          dragmode: "pan",
          font: { family: "Sans Serif", size: 10 },
          margin: { b: 55, t: 50, r: 50, l: 50 },
          modebar: {
            remove: ["autoScale2d", "lasso", "lasso2d", "toImage", "select2d"],
          },
          plot_bgcolor: "white",
          title: {
            x: 0.5,
            xanchor: "center",
            y: 0.95,
            yanchor: "top",
          },
          yaxis: { gridcolor: "lightgrey", zerolinecolor: "lightgrey" },
        },
      },
    },
  };

  const [plot, updatePlot] = useState(initialPlot);
  const [prevTitle] = useState(initialPlot.layout.title.text);

  useEffect(() => {
    const displaySizes = computeDisplaySizes();
    setComputedSettings({
      width: displaySizes.width,
      height: displaySizes.height,
      titleSize: displaySizes.titleSize,
      textSize: displaySizes.textSize,
    });
    updatePlot((prevPlot) => ({
      ...prevPlot,
      layout: {
        ...prevPlot.layout,
        width: displaySizes.width,
        height: displaySizes.height,
        title: {
          font: {
            family: settings.selectedFont,
            size: displaySizes.titleSize,
          },
          text: settings.title ?? prevTitle,
        },
        template: {
          layout: {
            ...prevPlot.layout.template.layout,
            font: {
              ...prevPlot.layout.template.layout.font,
              family: settings.selectedFont,
              size: displaySizes.textSize,
            },
          },
        },
      },
    }));
    // TODO Fix this dependency issue
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prevTitle, settings]);

  const handleDownload = () => {
    void downloadPlot(plot as Figure);
    onClose();
  };
  const handleReset = () => {
    void loadSettings("plots_default");
    settings.title = prevTitle;
  };
  const handleSaving = () => {
    void saveSettings();
  };

  return (
    <StyledModal isOpen={isOpen} onClose={onClose} title="Download Plot">
      <SectionTitle
        baseComponent={"h6"}
        description={
          "All configurations entered here apply to this plot only. If you want to apply them to future plots, save them as your template."
        }
        style={{ paddingBottom: "20px" }}
      />

      <Row>
        <Col md={6}>
          <SettingsDiv>
            <SectionTitle baseComponent={"h5"} title={"Format and Size"} />
            <FileFormatField
              onChange={handleFileFormatChange}
              value={settings.fileFormat}
            />
            <Row justify="between" align="center">
              <Col>
                <WidthField
                  value={settings.width}
                  onChange={handleWidthChange}
                />
              </Col>
              <Col>
                <HeightField
                  value={settings.height}
                  onChange={handleHeightChange}
                />
              </Col>
            </Row>
            <SectionTitle
              baseComponent={"h5"}
              title={"Text"}
              style={{ paddingTop: "4px", paddingBottom: "4px" }}
            />
            <FontField
              selectedFont={settings.selectedFont}
              onChange={handleFontChange}
            />
            <CustomFontField
              selectedFont={settings.selectedFont}
              customFont={settings.customFont}
              onChange={handleCustomFontChange}
            />
            <Row justify="between" align="center">
              <Col>
                <TitleSizeField
                  onChange={handleTitleSizeChange}
                  value={settings.titleSize}
                />
              </Col>
              <Col>
                <TextSizeField
                  value={settings.textSize}
                  onChange={handleTextSizeChange}
                />
              </Col>
            </Row>
            <TextInputField
              onChange={handleTitleChange}
              label={"Title"}
              value={plot.layout.title.text}
            />
          </SettingsDiv>
        </Col>
        <Col md={6}>
          <PlotDiv>
            <PlotComponent
              styleProps={{ margin: "2px" }}
              data={plot.data as Partial<PlotData>[]}
              layout={plot.layout as Partial<Layout>}
              divId={"plot-id"}
            />
          </PlotDiv>
        </Col>
      </Row>
      <Footer>
        <SecondaryButton
          text={"Reset to default"}
          icon="reload"
          onPress={handleReset}
        />
        <SecondaryButton
          text="Save as template"
          icon="clipboard"
          onPress={handleSaving}
        />
        <Button text="Download plot" icon="download" onPress={handleDownload} />
      </Footer>
    </StyledModal>
  );
};
