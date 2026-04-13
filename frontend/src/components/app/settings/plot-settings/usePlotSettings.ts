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

  const loadSettings = async (templateName: string): Promise<PlotSettings | null> => {
    setIsLoading(true);
    try {
      const response = await callApiWithParameters("load_settings", {
        templateName: templateName,
      });
      if (!response) {
        return null;
      }

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
      return loadedSettings;
    } catch (error: unknown) {
      console.error("Loading plot settings failed: ", error);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      void loadSettings("plots");
    }
  }, [isOpen]);

  const saveSettings = async (settingsToSave: PlotSettings = settings): Promise<boolean> => {
    const res = await callApiWithParameters("save_settings", {
      file_format: settingsToSave.fileFormat,
      width: settingsToSave.width,
      height: settingsToSave.height,
      margin_top: settingsToSave.marginTop,
      margin_bottom: settingsToSave.marginBottom,
      margin_left: settingsToSave.marginLeft,
      margin_right: settingsToSave.marginRight,
      font: settingsToSave.selectedFont,
      custom_font: settingsToSave.customFont,
      title_size: settingsToSave.titleSize,
      text_size: settingsToSave.textSize,
    });
    if (res?.success) {
      setSavedSettings(settingsToSave);
      notify({
        title: "Saved successfully",
        message: "Your settings will apply to all plots you want to download.",
        type: "success",
      });
      return true;
    } else {
      notify({
        title: "Saving failed",
        message: "An unexpected error occurred.",
        type: "error",
      });
      return false;
    }
  };

  const resetSettingsToDefault = async (): Promise<boolean> => {
    const defaultSettings = await loadSettings("plots_default");
    if (!defaultSettings) {
      notify({
        title: "Reset failed",
        message: "Could not load default settings.",
        type: "error",
      });
      return false;
    }
    return saveSettings(defaultSettings);
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
      const blob = (await callApiWithParameters(
        "download_plot",
        {
          plot: plotAsJson,
          fileFormat: settings.fileFormat,
          scale: scale,
        },
        "blob",
      ).catch((error: unknown) => {
        console.error("Export as .", settings.fileFormat, " failed: ", error);
        return undefined;
      })) as Blob | undefined;
      if (!blob) {
        notify({
          title: "Download failed",
          message: "Could not export the plot.",
          type: "error",
        });
        return;
      }
      const fileNameWithSuffix = fileName + "." + settings.fileFormat;
      saveAs(blob, fileNameWithSuffix);
    } else {
      console.error("Downloading plot as .", settings.fileFormat, " is not implemented.");
    }
  };

  const ptToInch = 1 / 72;
  const inchToMm = 25.4;
  const exportDpi = 300;
  const screenDpi = 96;

  /**
   * This function returns the scale factor for resizing the plot from its
   * current displayed size to desired download size (regarding resolution etc).
   */
  const getScale = (plot: Figure) => {
    const currentWidth = plot.layout.width ?? Math.round((settings.width / inchToMm) * screenDpi);
    return ((settings.width / inchToMm) * exportDpi) / currentWidth;
  };

  /**
   * This function returns the sizes for displaying the plot at screen DPI,
   * preserving detail that would be lost with a fixed small preview width.
   */
  const computeDisplaySizes = () => {
    // Figure size at screen resolution
    const width = Math.round((settings.width / inchToMm) * screenDpi);
    const height = Math.round((settings.height / inchToMm) * screenDpi);
    // Font size: convert pt to screen pixels (pt → inch → pixels at screen DPI)
    const titleSize = Math.round(settings.titleSize * ptToInch * screenDpi);
    const textSize = Math.round(settings.textSize * ptToInch * screenDpi);
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
    resetSettingsToDefault,
    downloadPlot,
    computeDisplaySizes,
    getTitleFromLayout,
    handleSettingChange,
    handleFontChange,
    handleCustomFontChange,
  };
};
