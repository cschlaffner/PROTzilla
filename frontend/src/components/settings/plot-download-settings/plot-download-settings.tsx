import { Layout, PlotData } from "plotly.js";
import Plotly from "plotly.js-dist-min";
import { useEffect, useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled } from "styled-components";

import { PlotDownloadSettingsProps } from "./plot-download-settings.props";
import {
  Button,
  DropdownInputField,
  Modal,
  NumberInputField,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  Text,
  TextInputField,
} from "../../../components";
import {
  border,
  borderColors,
  color,
  fontSize,
  fontWeight,
  spacing,
} from "../../../theme";
import { usePlotSettings } from "../specific-settings/usePlotSettings";

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

const Label = styled(Text)`
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("bold")};
  color: ${color("primary")};
  margin: 4px 0;
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
    const sizeRatio = settings.width / settings.height;
    const displayedWidth = 400;
    const displayedHeight = Math.round(displayedWidth / sizeRatio);
    updatePlot((prevPlot) => ({
      ...prevPlot,
      layout: {
        ...prevPlot.layout,
        width: displayedWidth,
        height: displayedHeight,
        title: {
          font: {
            family: settings.selectedFont,
            size: settings.titleSize,
          },
          text: settings.title ?? prevTitle,
        },
        template: {
          layout: {
            ...prevPlot.layout.template.layout,
            font: {
              ...prevPlot.layout.template.layout.font,
              family: settings.selectedFont,
              size: settings.textSize,
            },
          },
        },
      },
    }));
  }, [prevTitle, settings]);

  const handleDownload = () => {
    Plotly.downloadImage("plot-id", {
      format: settings.fileFormat,
      filename: "testfile",
      width: 400,
      height: 250,
      scale: 10,
    } as Plotly.DownloadImgopts).catch((error: unknown) => {
      console.error("Export failed: ", error);
    });
  };

  const handleReset = () => {
    void loadSettings();
    settings.title = prevTitle;
  };

  const fonts = [
    "Arial",
    "Courier New",
    "Helvetica",
    "Sans Serif",
    "Times New Roman",
  ];
  const isCustomSelected = !fonts.includes(settings.selectedFont);

  return (
    <StyledModal isOpen={isOpen} onClose={onClose} title="Download Plots">
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
            <DropdownInputField
              options={[
                { value: "eps", label: "eps" },
                { value: "jpg", label: "jpg" },
                { value: "pdf", label: "pdf" },
                { value: "png", label: "png" },
                { value: "svg", label: "svg" },
                { value: "tiff", label: "tiff" },
              ]}
              onChange={handleFileFormatChange}
              label={"File format"}
              value={settings.fileFormat}
            />
            <Row justify="between" align="center">
              <Col>
                <NumberInputField
                  label={"Width"}
                  min={10}
                  max={300}
                  step={1}
                  hasStepButtons={true}
                  separateSuffix={"mm"}
                  isInteger={true}
                  onChange={handleWidthChange}
                  value={settings.width}
                />
              </Col>
              <Col>
                <NumberInputField
                  label={"Height"}
                  min={10}
                  max={300}
                  step={1}
                  hasStepButtons={true}
                  separateSuffix={"mm"}
                  isInteger={true}
                  onChange={handleHeightChange}
                  value={settings.height}
                />
              </Col>
            </Row>
            <SectionTitle
              baseComponent={"h5"}
              title={"Text"}
              style={{ paddingTop: "4px", paddingBottom: "4px" }}
            />
            <div>
              <Label text={"Font"} />
              <div
                style={{ display: "flex", gap: "1rem", alignItems: "center" }}
              >
                {fonts.map((font) => {
                  const formattedId = `radio${font.replace(/\s/g, "")}`;
                  return (
                    <div
                      key={font}
                      style={{ display: "flex", alignItems: "center" }}
                    >
                      <input
                        type="radio"
                        id={formattedId}
                        name="fontGroup"
                        value={font}
                        checked={settings.selectedFont === font}
                        onChange={handleFontChange}
                      />
                      <label htmlFor={formattedId}>{font}</label>
                    </div>
                  );
                })}
              </div>
              <div
                style={{ display: "flex", gap: "1rem", alignItems: "center" }}
              >
                <div>
                  <input
                    type="radio"
                    id={"radioCustomFont"}
                    name="fontGroup"
                    value="Custom font"
                    checked={isCustomSelected}
                    onChange={handleFontChange}
                  />
                  <label htmlFor={"radioCustomFont"}>{"Custom font:"}</label>
                </div>
                <div style={{ flexGrow: 1 }}>
                  <TextInputField
                    placeholder="Custom font name"
                    onChange={handleCustomFontChange}
                    value={settings.customFont}
                  />
                </div>
              </div>
            </div>
            <Row justify="between" align="center">
              <Col>
                <NumberInputField
                  label={"Title size"}
                  min={1}
                  max={100}
                  step={1}
                  hasStepButtons={true}
                  separateSuffix={"pt"}
                  isInteger={true}
                  onChange={handleTitleSizeChange}
                  value={settings.titleSize}
                />
              </Col>
              <Col>
                <NumberInputField
                  label={"Text size"}
                  min={1}
                  max={100}
                  step={1}
                  hasStepButtons={true}
                  separateSuffix={"pt"}
                  isInteger={true}
                  onChange={handleTextSizeChange}
                  value={settings.textSize}
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
          onPress={void saveSettings}
        />
        <Button text="Download plot" icon="download" onPress={handleDownload} />
      </Footer>
    </StyledModal>
  );
};
