// This is a custom hook for working with plot settings.

import { useNotification } from "@protzilla/app";
import { callApiWithParameters } from "@protzilla/utils";
import { saveAs } from "file-saver";
import { Figure, Layout } from "plotly.js";
import Plotly from "plotly.js-dist-min";
import { useEffect, useState } from "react";

export interface PlotSettings {
  // User-given parameters that are stored in backend
  fileFormat: string;
  width: number;
  height: number;
  marginTop: number;
  marginBottom: number;
  marginLeft: number;
  marginRight: number;
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
  const notify = useNotification();

  const [isLoading, setIsLoading] = useState<boolean>(true);
  // Since null is not allowed, these settings are used for rendering.
  const emptySettings: PlotSettings = {
    fileFormat: "",
    width: 0,
    height: 0,
    marginTop: 0,
    marginBottom: 0,
    marginLeft: 0,
    marginRight: 0,
    selectedFont: "",
    customFont: "",
    titleSize: 0,
    textSize: 0,

    title: "",
  };
  const [settings, setSettings] = useState<PlotSettings>(emptySettings);
  const [savedSettings, setSavedSettings] = useState<PlotSettings>(emptySettings);
  const [computedSettings, setComputedSettings] = useState<ComputedPlotSettings>({
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
      const loadedSettings: PlotSettings = {
        fileFormat: response.file_format,
        width: response.width,
        height: response.height,
        marginTop: response.margin_top,
        marginBottom: response.margin_bottom,
        marginLeft: response.margin_left,
        marginRight: response.margin_right,
        selectedFont: response.font,
        customFont: response.custom_font,
        titleSize: response.title_size,
        textSize: response.text_size,
      };
      setSettings(loadedSettings);
      setSavedSettings(loadedSettings);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (isOpen) {
      void loadSettings("plots");
    }
  }, [isOpen]);

  const saveSettings = async () => {
    setSavedSettings(settings);
    const res = await callApiWithParameters("save_settings", {
      file_format: settings.fileFormat,
      width: settings.width,
      height: settings.height,
      margin_top: settings.marginTop,
      margin_bottom: settings.marginBottom,
      margin_left: settings.marginLeft,
      margin_right: settings.marginRight,
      font: settings.selectedFont,
      custom_font: settings.customFont,
      title_size: settings.titleSize,
      text_size: settings.textSize,
    });
    if (res?.success) {
      notify({
        title: "Saved successfully",
        message: "Your settings will apply to all plots you want to download.",
        type: "success",
      });
    } else {
      notify({
        title: "Saving failed",
        message: "An unexpected error occurred.",
        type: "error",
      });
    }
  };

  const downloadPlot = async (plot: Figure) => {
    // TODO Part of issue #36: Customize file name
    const fileName = "plot";
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
      console.error("Downloading plot as .", settings.fileFormat, " is not implemented.");
    }
  };

  // Fixed width for containing the correct ratio of width & height
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
    const titleSize = Math.round(settings.titleSize * ptToInch * inchToMm * ratio);
    const textSize = Math.round(settings.textSize * ptToInch * inchToMm * ratio);
    return {
      width,
      height,
      titleSize,
      textSize,
    };
  };

  /**
   * Because Plotly allows title to be a string or object of text & font
   */
  const getTitleFromLayout = (layout: Partial<Layout>) => {
    const titleProp = layout.title;
    if (titleProp == null) {
      return "";
    }
    if (typeof titleProp === "string") {
      return titleProp;
    }
    return titleProp.text ?? "";
  };

  // Handle functions
  /**
   * This function is used as generic handler if there are no side effects
   */
  const handleSettingChange = <K extends keyof PlotSettings>(key: K, value: PlotSettings[K]) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };
  const handleFontChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSettings((prev) => ({
      ...prev,
      selectedFont: value,
    }));
  };
  const handleCustomFontChange = (value: string, isCustomSelected: boolean) => {
    setSettings((prev) => ({
      ...prev,
      customFont: value,
    }));
    if (isCustomSelected) {
      setSettings((prev) => ({
        ...prev,
        selectedFont: value,
      }));
    }
  };

  return {
    isLoading,
    settings,
    savedSettings,
    computedSettings,
    setSettings,
    setComputedSettings,
    loadSettings,
    saveSettings,
    downloadPlot,
    computeDisplaySizes,
    getTitleFromLayout,
    handleSettingChange,
    handleFontChange,
    handleCustomFontChange,
  };
};
