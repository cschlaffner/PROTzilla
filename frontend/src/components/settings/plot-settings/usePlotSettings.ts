// This is a custom hook for working with plot settings.

import { saveAs } from "file-saver";
import { Figure } from "plotly.js";
import Plotly from "plotly.js-dist-min";
import { useEffect, useState } from "react";

import { callApiWithParameters } from "../../../utils";

export interface PlotSettings {
  fileFormat: string;
  width: number;
  height: number;
  selectedFont: string;
  customFont: string;
  titleSize: number;
  textSize: number;
  // The following parameters are only relevant for the "Plot Download" modal and are therefore optional.
  title?: string;
}

export const usePlotSettings = (isOpen: boolean) => {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [settings, setSettings] = useState<PlotSettings>({
    fileFormat: "",
    width: 0,
    height: 0,
    selectedFont: "",
    customFont: "",
    titleSize: 0,
    textSize: 0,
    title: "",
  });

  const loadSettings = async (templateName: string) => {
    const response = await callApiWithParameters("load_settings", {
      templateName: templateName,
    });
    if (response) {
      setSettings({
        fileFormat: response.file_format,
        width: response.width,
        height: response.height,
        selectedFont: response.font,
        customFont: response.custom_font,
        titleSize: response.title_size,
        textSize: response.text_size,
      });
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (isOpen) {
      void loadSettings("plots");
    }
  }, [isOpen]);

  const saveSettings = async () => {
    await callApiWithParameters("save_settings", {
      file_format: settings.fileFormat,
      width: settings.width,
      height: settings.height,
      font: settings.selectedFont,
      custom_font: settings.customFont,
      title_size: settings.titleSize,
      text_size: settings.textSize,
    });
  };

  const downloadPlot = async (plot: Figure) => {
    // TODO: Get filename from run, calculate experienced sizes & scale
    const fileName = "testfile";
    const width = plot.layout.width;
    const height = plot.layout.height;
    const scale = 10;
    const plotAsJson = JSON.stringify(plot);

    if (["jpeg", "png", "svg", "webp"].includes(settings.fileFormat)) {
      Plotly.downloadImage("plot-id", {
        format: settings.fileFormat,
        filename: fileName,
        width: width,
        height: height,
        scale: scale,
      } as Plotly.DownloadImgopts).catch((error: unknown) => {
        console.error("Export as .", settings.fileFormat, " failed: ", error);
      });
    } else if (["eps", "pdf", "tiff"].includes(settings.fileFormat)) {
      const blob: Blob = await callApiWithParameters(
        "download_plot",
        {
          plot: plotAsJson,
          fileFormat: settings.fileFormat,
          scale: scale,
        },
        "blob",
      ).catch((error: unknown) => {
        console.error("Export as .", settings.fileFormat, " failed: ", error);
      });
      const fileNameWithSuffix = fileName + "." + settings.fileFormat;
      saveAs(blob, fileNameWithSuffix);
    } else {
      console.error(
        "Downloading plot as .",
        settings.fileFormat,
        " is not implemented.",
      );
    }
  };

  // Handle functions for input fields regarding the plot settings
  const handleFileFormatChange = (value: string) => {
    setSettings((prev) => ({
      ...prev,
      fileFormat: value,
    }));
  };
  const handleWidthChange = (value: number) => {
    setSettings((prev) => ({
      ...prev,
      width: value,
    }));
  };
  const handleHeightChange = (value: number) => {
    setSettings((prev) => ({
      ...prev,
      height: value,
    }));
  };
  const handleFontChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newFont =
      event.target.value === "Custom font"
        ? settings.customFont
        : event.target.value;
    setSettings((prev) => ({
      ...prev,
      selectedFont: newFont,
    }));
  };
  const handleCustomFontChange = (value: string) => {
    setSettings((prev) => ({
      ...prev,
      customFont: value,
    }));
  };
  const handleTitleSizeChange = (value: number) => {
    setSettings((prev) => ({
      ...prev,
      titleSize: value,
    }));
  };
  const handleTextSizeChange = (value: number) => {
    setSettings((prev) => ({
      ...prev,
      textSize: value,
    }));
  };
  const handleTitleChange = (value: string) => {
    setSettings((prev) => ({
      ...prev,
      title: value,
    }));
  };

  // TODO Include resizing & scaling from PROTzilla2

  // # SCALED_WIDTH = 600
  // # PT_TO_INCH = 1 / 72
  // # INCH_TO_MM = 25.4
  // # DPI = 300

  //   def resize_for_display(params: dict) -> dict:
  //     """
  //     Scales the input sizes to sizes that can be easily displayed in a webbrowser.
  //     :param params: Dict containing the plot settings.
  //     :return: Dict containing plot settings with scaled sizes.
  //     """
  //     # Figure size
  //     ratio = params["width"] / params["height"]
  //     display_height = int(SCALED_WIDTH / ratio)
  //     # Font size
  //     ratio = SCALED_WIDTH / params["width"]
  //     display_heading = int(params["heading_size"] * PT_TO_INCH * INCH_TO_MM * ratio)
  //     display_text = int(params["text_size"] * PT_TO_INCH * INCH_TO_MM * ratio)
  //     params["display_width"] = SCALED_WIDTH
  //     params["display_height"] = display_height
  //     params["display_heading_size"] = display_heading
  //     params["display_text_size"] = display_text
  //     return params

  // def get_scale_factor(
  //         fig: go.Figure,
  //         params: dict
  //     ) -> float:
  //     """
  //     Calculates the scale factor for downloading the plot in desired size and resolution.
  //     :param fig: Plotly figure to be scaled.
  //     :param params: Dict containing the plot settings.
  //     :return: Scale factor to scale the whole plot to desired size.
  //     """
  //     current_width = fig.layout.width or SCALED_WIDTH
  //     scale_factor = (params["width"] / INCH_TO_MM * DPI) / current_width
  //     return scale_factor

  return {
    isLoading,
    settings,
    setSettings,
    loadSettings,
    saveSettings,
    downloadPlot,
    handleFileFormatChange,
    handleWidthChange,
    handleHeightChange,
    handleFontChange,
    handleCustomFontChange,
    handleTitleSizeChange,
    handleTextSizeChange,
    handleTitleChange,
  };
};
