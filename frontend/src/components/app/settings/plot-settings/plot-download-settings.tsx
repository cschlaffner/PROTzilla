import { color, spacing, zIndex } from "@protzilla/theme";
import { callApiWithParameters } from "@protzilla/utils";
import { Data, Figure, Layout, Plots } from "plotly.js-dist-min";
import { useEffect, useRef, useState } from "react";
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
import { hasFixedLayout, PlotSettings, usePlotSettings } from "./usePlotSettings";
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
  // Needed to re-render fixed-layout plots (see hasFixedLayout) at the chosen size
  runName?: string;
  // Position of the plot among the plots of the current step
  plotIndex?: number;
}

// Wait for the user to stop typing before a fixed-layout plot is rendered again
const RERENDER_DEBOUNCE_MS = 400;

export const PlotDownloadSettings: React.FC<PlotDownloadSettingsProps> = ({
  isOpen,
  onClose,
  data,
  layout,
  runName,
  plotIndex = 0,
}) => {
  const {
    isLoading,
    settings,
    resetSettingsToDefault,
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

  // A fixed-layout figure cannot be stretched in the browser, so width, height, font and text
  // size are applied by rendering it again in the backend (without touching the stored run).
  const isFixed = hasFixedLayout(layout);
  const canRerender = isFixed && runName !== undefined;
  const [isRendering, setIsRendering] = useState(false);
  const [renderError, setRenderError] = useState<string | undefined>();
  const latestRenderRequest = useRef(0);

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
    // A fixed-layout figure (see hasFixedLayout) encodes its geometry in its own canvas
    // size and draws its margins inside the data area, so resizing or re-margining it here
    // would pull the geometry away from the text. Size and font are chosen when the step is
    // calculated; only the title stays editable.
    setPlot({
      data: plot.data,
      layout: {
        ...plot.layout,
        ...(isFixed
          ? {}
          : {
              width: displaySizes.width,
              height: displaySizes.height,
              margin: {
                ...plot.layout.margin,
                t: settings.marginTop,
                b: settings.marginBottom,
                l: settings.marginLeft,
                r: settings.marginRight,
              },
              font: {
                ...plot.layout.font,
                family: settings.selectedFont,
                size: displaySizes.textSize,
              },
            }),
        title: {
          font: {
            family: settings.selectedFont,
            size: displaySizes.titleSize,
          },
          text: settings.title ?? prevTitle,
        },
      },
    });
    if (plotDiv) {
      Plots.resize(plotDiv);
    }
    // Only include variables, used functions will not change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prevTitle, settings]);

  useEffect(() => {
    if (!isOpen || !canRerender || isLoading) {
      setIsRendering(false);
      return;
    }
    if (!settings.width || !settings.height || !settings.textSize) {
      return;
    }
    const requestId = ++latestRenderRequest.current;
    setIsRendering(true);
    const timer = setTimeout(() => {
      void callApiWithParameters("rerender_plot/", {
        run_name: runName,
        plot_settings: {
          width: settings.width,
          height: settings.height,
          text_size: settings.textSize,
          font: settings.selectedFont,
        },
      })
        .then((response?: { success?: boolean; message?: string; data?: string[] }) => {
          // A newer request was started in the meantime, its result wins
          if (requestId !== latestRenderRequest.current) return;
          const renderedPlot = response?.data?.[plotIndex];
          if (response?.success && renderedPlot) {
            const figure = JSON.parse(renderedPlot) as Figure;
            setPlot((prev) => ({
              data: figure.data,
              layout: { ...figure.layout, title: prev.layout.title },
            }));
            setRenderError(undefined);
          } else {
            setRenderError(response?.message ?? "The plot could not be rendered at this size.");
          }
        })
        .finally(() => {
          if (requestId === latestRenderRequest.current) setIsRendering(false);
        });
    }, RERENDER_DEBOUNCE_MS);
    return () => {
      clearTimeout(timer);
    };
  }, [
    isOpen,
    canRerender,
    isLoading,
    runName,
    plotIndex,
    settings.width,
    settings.height,
    settings.textSize,
    settings.selectedFont,
  ]);

  const handleDownload = () => {
    void downloadPlot(plot as Figure);
    onClose();
  };
  const handleReset = () => {
    void (async () => {
      const hasReset = await resetSettingsToDefault();
      if (hasReset) {
        handleSettingChange("title", prevTitle);
      }
    })();
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
            {isFixed ? (
              <SectionTitle
                baseComponent={"h6"}
                description={
                  "This plot is laid out for the chosen size and text size and is rendered again when they change. Margins don't apply to it."
                }
              />
            ) : (
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
            )}
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
          <StyledDiv style={{ opacity: isRendering ? 0.5 : 1 }}>
            {renderError && <SectionTitle baseComponent={"h6"} description={renderError} />}
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
        <Button
          text={isRendering ? "Rendering plot…" : "Download plot"}
          icon="download"
          onPress={handleDownload}
          // The preview must match the chosen size before a fixed-layout plot is exported
          isDisabled={canRerender && (isRendering || renderError !== undefined)}
        />
      </Footer>
    </StyledModal>
  );
};
