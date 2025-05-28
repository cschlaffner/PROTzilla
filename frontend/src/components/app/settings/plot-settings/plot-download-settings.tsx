import { color, spacing, zIndex } from "@protzilla/theme";
import { Data, Figure, Layout } from "plotly.js";
import { useEffect, useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled } from "styled-components";

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
import {
  Button,
  Modal,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  TextInputField,
} from "../../../core/";

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
    settings,
    loadSettings,
    saveSettings,
    computeDisplaySizes,
    setComputedSettings,
    downloadPlot,
    getTitleFromLayout,
    handleFileFormatChange,
    handleWidthChange,
    handleHeightChange,
    handleFontChange,
    handleCustomFontChange,
    handleTitleSizeChange,
    handleTextSizeChange,
    handleTitleChange,
  } = usePlotSettings(isOpen);

  const initialPlot = { data, layout };
  const [plot, updatePlot] = useState(initialPlot);
  const [prevTitle] = useState<string>(getTitleFromLayout(initialPlot.layout));

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
        font: {
          ...prevPlot.layout.font,
          family: settings.selectedFont,
          size: displaySizes.textSize,
        },
      },
    }));
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
            <FileFormatField onChange={handleFileFormatChange} value={settings.fileFormat} />
            <Row justify="between" align="center">
              <Col>
                <WidthField value={settings.width} onChange={handleWidthChange} />
              </Col>
              <Col>
                <HeightField value={settings.height} onChange={handleHeightChange} />
              </Col>
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
                <TitleSizeField onChange={handleTitleSizeChange} value={settings.titleSize} />
              </Col>
              <Col>
                <TextSizeField value={settings.textSize} onChange={handleTextSizeChange} />
              </Col>
            </Row>
            <TextInputField
              onChange={handleTitleChange}
              label={"Title"}
              value={getTitleFromLayout(plot.layout)}
            />
          </SettingsDiv>
        </Col>
        <Col md={6}>
          <PlotComponent
            data={plot.data}
            layout={plot.layout}
            hasBorder={true}
            hasResizing={false}
            divId={"plot-id"}
          />
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
