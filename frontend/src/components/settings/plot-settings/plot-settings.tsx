import { Layout, PlotData } from "plotly.js";
import { useEffect, useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled, useTheme } from "styled-components";

import { usePlotSettings } from "./usePlotSettings";
import {
  Button,
  DropdownInputField,
  NumberInputField,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  Text,
  TextInputField,
} from "../..";
import { PlotDownloadSettings } from "./plot-download-settings";
import { useToggleableState } from "../../../hooks";
import {
  border,
  borderColors,
  color,
  fontSize,
  fontWeight,
  spacing,
} from "../../../theme";

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
`;

const Footer = styled.div`
  position: absolute;
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

const Label = styled(Text)`
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("bold")};
  color: ${color("primary")};
  margin: 4px 0;
`;

const StyledRadio = styled.input.attrs({ type: "radio" })`
  accent-color: ${color("primary")};
  margin-right: ${spacing("superSmall")};
`;

interface PlotSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PlotSettings: React.FC<PlotSettingsProps> = ({
  isOpen,
  onClose,
}) => {
  // TODO Remove, this is only for testing
  const [isDownloadOpen, openDownload, closeDownload] =
    useToggleableState(false);
  const handleOpenDownload = () => {
    openDownload();
  };

  const {
    settings,
    saveSettings,
    setComputedSettings,
    isLoading,
    loadSettings,
    computeDisplaySizes,
    handleFileFormatChange,
    handleWidthChange,
    handleHeightChange,
    handleFontChange,
    handleCustomFontChange,
    handleTitleSizeChange,
    handleTextSizeChange,
  } = usePlotSettings(isOpen);

  const theme = useTheme();

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
          ...prevPlot.layout.template.layout.title,
          font: {
            ...prevPlot.layout.template.layout.title,
            family: settings.selectedFont,
            size: displaySizes.titleSize,
          },
          text: prevPlot.layout.title.text,
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
  }, [settings]);

  const handleSaving = (
    event:
      | React.PointerEvent<HTMLButtonElement>
      | React.KeyboardEvent<HTMLButtonElement>,
  ) => {
    const target = event.currentTarget;
    void saveSettings();
    if (target.id == "saveAndQuit") {
      onClose();
    }
  };

  const handleReset = () => {
    void loadSettings("plots_default");
  };

  const fonts = [
    "Arial",
    "Courier New",
    "Helvetica",
    "Sans Serif",
    "Times New Roman",
  ];
  const isCustomSelected = !fonts.includes(settings.selectedFont);

  if (isLoading) {
    return (
      <SectionTitle
        baseComponent={"h6"}
        description={"Loading plot export settings ..."}
        style={{ paddingBottom: "20px" }}
      />
    );
  }

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Configurations for Plot Exports"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={
          "The configurations made here are automatically applied to all plots that will be exported with PROTzilla."
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
                { value: "jpeg", label: "jpeg" },
                { value: "pdf", label: "pdf" },
                { value: "png", label: "png" },
                { value: "svg", label: "svg" },
                { value: "tiff", label: "tiff" },
                { value: "webp", label: "webp" },
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
                      <StyledRadio
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
                style={{
                  display: "flex",
                  gap: theme.spacing.small,
                  alignItems: "center",
                }}
              >
                <div>
                  <StyledRadio
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
          </SettingsDiv>
        </Col>
        <Col md={6}>
          <PlotDiv>
            <PlotComponent
              styleProps={{ margin: "2px" }}
              data={plot.data as Partial<PlotData>[]}
              layout={plot.layout as Partial<Layout>}
            />
          </PlotDiv>
        </Col>
      </Row>
      <Footer>
        {/* TODO Remove this */}
        <Button text="<Download Modal>" onPress={handleOpenDownload} />
        <SecondaryButton
          text={"Reset to default"}
          icon="reload"
          onPress={handleReset}
        />
        <SecondaryButton
          id="save"
          text={"Save"}
          onPress={(event) => {
            handleSaving(event);
          }}
        />
        <Button
          id="saveAndQuit"
          text={"Save & Quit"}
          onPress={(event) => {
            handleSaving(event);
          }}
        />
      </Footer>
      {/* TODO Remove this */}
      <PlotDownloadSettings isOpen={isDownloadOpen} onClose={closeDownload} />
    </div>
  );
};
