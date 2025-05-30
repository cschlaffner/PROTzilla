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
  MarginField,
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
    handleMarginTopChange,
    handleMarginBottomChange,
    handleMarginLeftChange,
    handleMarginRightChange,
    handleFontChange,
    handleCustomFontChange,
    handleTitleSizeChange,
    handleTextSizeChange,
    handleTitleChange,
  } = usePlotSettings(isOpen);

  const [plot, setPlot] = useState({ data, layout });
  // For keeping the original title of the plot
  const [prevTitle, setPrevTitle] = useState(() => getTitleFromLayout(layout));

  useEffect(() => {
    setPlot({ data, layout });
    setPrevTitle(getTitleFromLayout(layout));
    // Only include variables, used functions will not change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, layout]);

  useEffect(() => {
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
        <Col md={7}>
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
              subscript={
                "You can use basic HTML tags for formatting. For example, <b>Title</b> appears as bold text."
              }
            />
          </SettingsDiv>
        </Col>
        <Col md={5}>
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
