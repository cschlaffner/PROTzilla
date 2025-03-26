export const enum Sections {
  Importing = "importing",
  DataPreprocessing = "data_preprocessing",
  DataAnalysis = "data_analysis",
  DataIntegration = "data_integration",
}

export type Section = {
  id: string;
  name: string;
  steps: string[];
};
