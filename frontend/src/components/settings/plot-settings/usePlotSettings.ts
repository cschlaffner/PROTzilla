// This is a custom hook for working with plot settings.

import { saveAs } from "file-saver";
import { Figure } from "plotly.js";
import Plotly from "plotly.js-dist-min";
import { useEffect, useState } from "react";

import { callApiWithParameters } from "../../../utils";

export interface PlotSettings {
  // User-given parameters that are stored in backend
  fileFormat: string;
  width: number;
  height: number;
  selectedFont: string;
  customFont: string;
  titleSize: number;
  textSize: number;
  // Optional parameters, only relevant for "Plot Download" modal
  title?: string;
}

export interface ComputedPlotSettings {
  // Computed parameters for displaying the right sizes within the plot
  height?: number;
  width?: number;
  titleSize?: number;
  textSize?: number;
}

export const usePlotSettings = (isOpen?: boolean) => {
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
  const [computedSettings, setComputedSettings] =
    useState<ComputedPlotSettings>({
      width: 0,
      height: 0,
      titleSize: 0,
      textSize: 0,
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
    // TODO: Get filename from run or add input field for filename
    const fileName = "testfile";
    const scale = getScale(plot);
    const plotAsJson = JSON.stringify(plot);

    if (["jpeg", "png", "svg", "webp"].includes(settings.fileFormat)) {
      Plotly.downloadImage("plot-id", {
        format: settings.fileFormat,
        filename: fileName,
        width: computedSettings.width,
        height: computedSettings.height,
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

  const basePlotWidth = 400;
  const ptToInch = 1 / 72;
  const inchToMm = 25.4;
  const dpi = 300;

  /**
   * This function returns the scale factor for resizing the plot from its
   * current displayed size to desired download size (regarding resolution etc).
   */
  const getScale = (plot: Figure) => {
    const currentWidth = plot.layout.width ?? basePlotWidth;
    return ((settings.width / inchToMm) * dpi) / currentWidth;
  };

  /**
   * This function returns the scaled sizes for displaying the plot.
   */
  const computeDisplaySizes = () => {
    // Figure size
    let ratio = settings.width / settings.height;
    const width = basePlotWidth;
    const height = Math.round(basePlotWidth / ratio);
    // Font size
    ratio = width / settings.width;
    const titleSize = Math.round(
      settings.titleSize * ptToInch * inchToMm * ratio,
    );
    const textSize = Math.round(
      settings.textSize * ptToInch * inchToMm * ratio,
    );
    return {
      width,
      height,
      titleSize,
      textSize,
    };
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
    const value = event.target.value;
    setSettings((prev) => ({
      ...prev,
      selectedFont: value,
    }));
  };
  const handleCustomFontChange = (value: string) => {
    setSettings((prev) => ({
      ...prev,
      customFont: value,
      selectedFont: value,
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

  return {
    isLoading,
    settings,
    setSettings,
    computedSettings,
    setComputedSettings,
    loadSettings,
    saveSettings,
    downloadPlot,
    computeDisplaySizes,
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
