export interface SelectedStep {
  section: Sections;
  index: number;
}

export type SetSelectedStep = React.Dispatch<
  React.SetStateAction<SelectedStep | null>
>;

export type StepStatus = "complete" | "outdated" | "incomplete" | "failed";

export interface Step {
  id: string;
  name: string;
  method_name: string;
  status: StepStatus;
}

export const enum Sections {
  Importing = "importing",
  DataPreprocessing = "data_preprocessing",
  DataAnalysis = "data_analysis",
  DataIntegration = "data_integration",
}

export interface Section {
  id: Sections;
  name: string;
  steps: Step[];
}

export const emptySections: Section[] = [
  {
    id: Sections.Importing,
    name: "Importing",
    steps: [],
  },
  {
    id: Sections.DataPreprocessing,
    name: "Data Preprocessing",
    steps: [],
  },
  {
    id: Sections.DataAnalysis,
    name: "Data Analysis",
    steps: [],
  },
  {
    id: Sections.DataIntegration,
    name: "Data Integration",
    steps: [],
  },
];
