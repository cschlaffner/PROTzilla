// This is a custom hook for working with plot settings.

import { useEffect, useState } from "react";

import { callApi, callApiWithParameters } from "../../../utils";

export interface PlotSettings {
  fileFormat: string;
  width: number;
  height: number;
  selectedFont: string;
  customFont: string;
  headingSize: number;
  textSize: number;
  // The following parameters are only relevant for the "Plot Download" modal.
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
    headingSize: 0,
    textSize: 0,
  });

  const loadSettings = async () => {
    const response = await callApi("load_settings");
    if (response) {
      setSettings({
        fileFormat: response.file_format,
        width: response.width,
        height: response.height,
        selectedFont: response.font,
        customFont: response.custom_font,
        headingSize: response.heading_size,
        textSize: response.text_size,
      });
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (isOpen) {
      void loadSettings();
    }
  }, [isOpen]);

  const saveSettings = async () => {
    await callApiWithParameters("save_settings", {
      file_format: settings.fileFormat,
      // TODO Remove .toString() as soon as API can parse numbers
      width: settings.width.toString(),
      height: settings.height.toString(),
      font: settings.selectedFont,
      custom_font: settings.customFont,
      heading_size: settings.headingSize.toString(),
      text_size: settings.textSize.toString(),
    });
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
  const handleHeadingSizeChange = (value: number) => {
    setSettings((prev) => ({
      ...prev,
      headingSize: value,
    }));
  };
  const handleTextSizeChange = (value: number) => {
    setSettings((prev) => ({
      ...prev,
      textSize: value,
    }));
  };

  return {
    isLoading,
    settings,
    setSettings,
    loadSettings,
    saveSettings,
    handleFileFormatChange,
    handleWidthChange,
    handleHeightChange,
    handleFontChange,
    handleCustomFontChange,
    handleHeadingSizeChange,
    handleTextSizeChange,
  };
};
