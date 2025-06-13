import { Button, PlotComponent, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { color, fontSize, fontWeight, spacing, useTheme, zIndex } from "@protzilla/theme";
import isEqual from "fast-deep-equal";
import { Data, Layout, Plots } from "plotly.js-dist-min";
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
import { PlotSettings, usePlotSettings } from "./usePlotSettings";

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

export interface PlotSettingsModalProps {
  isOpen: boolean;
  onClose: (hasChanges: boolean) => void;
  setHasChanges: (hasChanges: boolean) => void;
}

export const PlotSettingsModal: React.FC<PlotSettingsModalProps> = ({
  isOpen,
  onClose,
  setHasChanges,
}) => {
  const {
    settings,
    savedSettings,
    saveSettings,
    setComputedSettings,
    isLoading,
    loadSettings,
    computeDisplaySizes,
    handleSettingChange,
    handleFontChange,
    handleCustomFontChange,
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
  const plotDivId = "plot-id";

  useEffect(() => {
    const plotDiv = document.getElementById(plotDivId);
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
    if (plotDiv) {
      Plots.resize(plotDiv);
    }
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

  const marginFields: {
    key: keyof PlotSettings;
    label: string;
    info?: string;
  }[] = [
    {
      key: "marginTop",
      label: "Margin, top",
      info: "Plots with axes include default margins, so margin changes below 50 may not be noticeable.",
    },
    { key: "marginBottom", label: "Bottom" },
    { key: "marginLeft", label: "Left" },
    { key: "marginRight", label: "Right" },
  ];

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
            <FileFormatField
              value={settings.fileFormat}
              onChange={(v: string | null) => {
                handleSettingChange("fileFormat", v ?? "");
              }}
            />
            <Row justify="between" align="center">
              <Col>
                <WidthField
                  value={settings.width}
                  onChange={(v: number) => {
                    handleSettingChange("width", v);
                  }}
                />
              </Col>
              <Col>
                <HeightField
                  value={settings.height}
                  onChange={(v: number) => {
                    handleSettingChange("height", v);
                  }}
                />
              </Col>
            </Row>
            <Row>
              {marginFields.map(({ key, label, info }) => (
                <Col key={key}>
                  <MarginField
                    label={label}
                    info={info}
                    value={settings[key] as number}
                    onChange={(v: number) => {
                      handleSettingChange(key, v);
                    }}
                  />
                </Col>
              ))}
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
                <TitleSizeField
                  value={settings.titleSize}
                  onChange={(v: number) => {
                    handleSettingChange("titleSize", v);
                  }}
                />
              </Col>
              <Col>
                <TextSizeField
                  value={settings.textSize}
                  onChange={(v: number) => {
                    handleSettingChange("textSize", v);
                  }}
                />
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
            divId={plotDivId}
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
