import { Button, PlotComponent, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { color, fontSize, fontWeight, spacing, useTheme, zIndex } from "@protzilla/theme";
import isEqual from "fast-deep-equal";
import { Data, Layout } from "plotly.js";
import { useEffect, useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled } from "styled-components";

import {
  CustomFontField,
  FileFormatField,
  FontField,
  HeightField,
  MarginField,
  TextSizeField,
  TitleSizeField,
  WidthField,
} from "./plot-settings-input-fields";
import { usePlotSettings } from "./usePlotSettings";

const SettingsDiv = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
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
  z-index: ${zIndex("modal")};
`;

const Label = styled(Text)`
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("bold")};
  color: ${color("primary")};
  margin: 4px 0;
`;

export interface PlotSettingsProps {
  isOpen: boolean;
  onClose: (hasChanges: boolean) => void;
  setHasChanges: (hasChanges: boolean) => void;
}

export const PlotSettings: React.FC<PlotSettingsProps> = ({ isOpen, onClose, setHasChanges }) => {
  const {
    settings,
    savedSettings,
    saveSettings,
    setComputedSettings,
    isLoading,
    loadSettings,
    computeDisplaySizes,
    handleFileFormatChange,
    handleWidthChange,
    handleHeightChange,
    handleMarginTopChange,
    handleMarginBottomChange,
    handleMarginLeftChange,
    handleMarginRightChange,
    handleFontChange,
    handleCustomFontChange,
    handleTitleSizeChange,
    handleTextSizeChange,
  } = usePlotSettings(isOpen);

  const theme = useTheme();

  const initialPlot = {
    data: [
      {
        x: ["Example 1"],
        y: [0.7],
        name: "Example 1",
        type: "bar",
        marker: {
          color: [theme.colors.protzillaDarkBlue],
        },
      },
      {
        x: ["Example 2"],
        y: [0.3],
        name: "Example 2",
        type: "bar",
        marker: {
          color: [theme.colors.protzillaRed],
        },
      },
    ],
    layout: {
      width: 400,
      height: 250,
      title: {
        font: { family: "Sans Serif", size: 15 },
        text: "Very important title",
      },
      margin: {
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
      },
      font: { family: "Sans Serif", size: 10 },
      xaxis: { anchor: "y", title: { text: "x-axis" }, automargin: true },
      yaxis: { anchor: "x", title: { text: "y-axis" }, automargin: true },
      showlegend: true,
    },
  };

  const [plot, setPlot] = useState(initialPlot);

  useEffect(() => {
    // Update settings
    const displaySizes = computeDisplaySizes();
    setComputedSettings({
      width: displaySizes.width,
      height: displaySizes.height,
      titleSize: displaySizes.titleSize,
      textSize: displaySizes.textSize,
    });
    setPlot((prevPlot) => ({
      ...prevPlot,
      layout: {
        ...prevPlot.layout,
        width: displaySizes.width,
        height: displaySizes.height,
        margin: {
          ...prevPlot.layout.margin,
          t: settings.marginTop,
          b: settings.marginBottom,
          l: settings.marginLeft,
          r: settings.marginRight,
        },
        title: {
          ...prevPlot.layout.title,
          font: {
            ...prevPlot.layout.title,
            family: settings.selectedFont,
            size: displaySizes.titleSize,
          },
          text: prevPlot.layout.title.text,
        },
        font: {
          ...prevPlot.layout.font,
          family: settings.selectedFont,
          size: displaySizes.textSize,
        },
      },
    }));
    // Update hasChanges flag for onClose action
    setHasChanges(!isEqual(settings, savedSettings));

    // Only include variables, used functions will not change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [savedSettings, settings]);

  const handleSaving = (
    event: React.PointerEvent<HTMLButtonElement> | React.KeyboardEvent<HTMLButtonElement>,
  ) => {
    const target = event.currentTarget;
    void saveSettings();
    if (target.id == "saveAndQuit") {
      onClose(false);
    }
  };

  const handleReset = () => {
    void loadSettings("plots_default");
  };

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
            <FileFormatField value={settings.fileFormat} onChange={handleFileFormatChange} />
            <Row justify="between" align="center">
              <Col>
                <WidthField value={settings.width} onChange={handleWidthChange} />
              </Col>
              <Col>
                <HeightField value={settings.height} onChange={handleHeightChange} />
              </Col>
            </Row>
            <Row>
              <Col>
                <MarginField
                  label={"Margins, top"}
                  value={settings.marginTop}
                  onChange={handleMarginTopChange}
                />
              </Col>
              <Col>
                <MarginField
                  label={"Bottom"}
                  value={settings.marginBottom}
                  onChange={handleMarginBottomChange}
                />
              </Col>
              <Col>
                <MarginField
                  label={"Left"}
                  value={settings.marginLeft}
                  onChange={handleMarginLeftChange}
                />
              </Col>
              <Col>
                <MarginField
                  label={"Right"}
                  value={settings.marginRight}
                  onChange={handleMarginRightChange}
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
              <FontField selectedFont={settings.selectedFont} onChange={handleFontChange} />
              <CustomFontField
                selectedFont={settings.selectedFont}
                customFont={settings.customFont}
                onRadioChange={handleFontChange}
                onTextChange={handleCustomFontChange}
              />
            </div>
            <Row justify="between" align="center">
              <Col>
                <TitleSizeField value={settings.titleSize} onChange={handleTitleSizeChange} />
              </Col>
              <Col>
                <TextSizeField value={settings.textSize} onChange={handleTextSizeChange} />
              </Col>
            </Row>
          </SettingsDiv>
        </Col>
        <Col md={6}>
          <PlotComponent
            data={plot.data as Data[]}
            layout={plot.layout as Partial<Layout>}
            hasBorder={true}
            hasResizing={false}
          />
        </Col>
      </Row>
      <Footer>
        <SecondaryButton text={"Reset to default"} icon="reload" onPress={handleReset} />
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
            setHasChanges(false);
            handleSaving(event);
          }}
        />
      </Footer>
    </div>
  );
};
