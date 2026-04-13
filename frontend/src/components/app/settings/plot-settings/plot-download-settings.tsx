import { color, spacing, zIndex } from "@protzilla/theme";
import { Data, Figure, Layout, Plots } from "plotly.js-dist-min";
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
import {
  Button,
  Modal,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  TextInputField,
} from "../../../core/";

const StyledModal = styled(Modal)`
  overflow: auto;
  max-width: 95vw;
  max-height: 95vh;
  width: 100%;
`;

const SettingsDiv = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

const StyledDiv = styled.div`
  overflow: auto;
  max-height: 70vh;
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
  z-index: ${zIndex("modal")};
`;

export interface PlotDownloadSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  data: Data[];
  layout: Partial<Layout>;
  runName?: string;
}

export const PlotDownloadSettings: React.FC<PlotDownloadSettingsProps> = ({
  isOpen,
  onClose,
  data,
  layout,
}) => {
  const {
    isLoading,
    settings,
    loadSettings,
    saveSettings,
    computeDisplaySizes,
    setComputedSettings,
    downloadPlot,
    getTitleFromLayout,
    handleSettingChange,
    handleFontChange,
    handleCustomFontChange,
  } = usePlotSettings(isOpen);

  const [plot, setPlot] = useState({ data, layout });
  const divId = "plot-id";
  // For keeping the original title of the plot
  const [prevTitle, setPrevTitle] = useState(() => getTitleFromLayout(layout));

  useEffect(() => {
    setPlot({ data, layout });
    setPrevTitle(getTitleFromLayout(layout));
    // Only include variables, used functions will not change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, layout]);

  useEffect(() => {
    const plotDiv = document.getElementById(divId);
    const displaySizes = computeDisplaySizes();
    setComputedSettings({
      width: displaySizes.width,
      height: displaySizes.height,
      titleSize: displaySizes.titleSize,
      textSize: displaySizes.textSize,
    });
    setPlot({
      data: plot.data,
      layout: {
        ...plot.layout,
        width: displaySizes.width,
        height: displaySizes.height,
        margin: {
          ...plot.layout.margin,
          t: settings.marginTop,
          b: settings.marginBottom,
          l: settings.marginLeft,
          r: settings.marginRight,
        },
        title: {
          font: {
            family: settings.selectedFont,
            size: displaySizes.titleSize,
          },
          text: settings.title ?? prevTitle,
        },
        font: {
          ...plot.layout.font,
          family: settings.selectedFont,
          size: displaySizes.textSize,
        },
      },
    });
    if (plotDiv) {
      Plots.resize(plotDiv);
    }
    // Only include variables, used functions will not change
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
    <StyledModal isOpen={isOpen} onClose={onClose} title="Download Plot">
      <SectionTitle
        baseComponent={"h6"}
        description={
          "All configurations entered here apply to this plot only. If you want to apply them to future plots, save them as your template."
        }
        style={{ paddingBottom: "20px" }}
      />

      <Row>
        <Col md={7}>
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
                  onChange={(value: number) => {
                    handleSettingChange("width", value);
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
            <FontField selectedFont={settings.selectedFont} onChange={handleFontChange} />
            <CustomFontField
              selectedFont={settings.selectedFont}
              customFont={settings.customFont}
              onRadioChange={handleFontChange}
              onTextChange={handleCustomFontChange}
            />
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
            <TextInputField
              onChange={(v: string) => {
                handleSettingChange("title", v);
              }}
              label={"Title"}
              value={getTitleFromLayout(plot.layout)}
              subscript={
                "You can use basic HTML tags for formatting. For example, <b>Title</b> appears as bold text."
              }
            />
          </SettingsDiv>
        </Col>
        <Col md={5}>
          <StyledDiv>
            {!isLoading && (
              <PlotComponent
                data={plot.data}
                layout={plot.layout}
                hasBorder={true}
                hasResizing={false}
                divId={divId}
              />
            )}
          </StyledDiv>
        </Col>
      </Row>
      <Footer>
        <SecondaryButton text={"Reset to default"} icon="reload" onPress={handleReset} />
        <SecondaryButton text="Save as template" icon="clipboard" onPress={handleSaving} />
        <Button text="Download plot" icon="download" onPress={handleDownload} />
      </Footer>
    </StyledModal>
  );
};
