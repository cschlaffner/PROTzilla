import { GridValidRowModel } from "@mui/x-data-grid";

export interface UIStateProps {
  isDisabled?: boolean;
}

export interface SelectedStep {
  section: SectionIDs;
  index: number;
}

export type StepStatus = "complete" | "outdated" | "incomplete" | "failed";

export interface Step {
  id: string;
  name: string;
  method_name: string;
  status: StepStatus;
}

export const enum SectionIDs {
  Importing = "importing",
  DataPreprocessing = "data_preprocessing",
  DataAnalysis = "data_analysis",
  DataIntegration = "data_integration",
}

export interface Section {
  id: SectionIDs;
  name: string;
  steps: Step[];
}

export const emptySections: Section[] = [
  {
    id: SectionIDs.Importing,
    name: "Importing",
    steps: [],
  },
  {
    id: SectionIDs.DataPreprocessing,
    name: "Data Preprocessing",
    steps: [],
  },
  {
    id: SectionIDs.DataAnalysis,
    name: "Data Analysis",
    steps: [],
  },
  {
    id: SectionIDs.DataIntegration,
    name: "Data Integration",
    steps: [],
  },
];

export interface Run {
  run_name: string;
  creation_date: string;
  modification_date: string;
  memory_mode: string;
  run_steps: string[];
  favourite_status: boolean;
  run_tags: string[];
}

export interface RunData {
  current_section: string;
  current_step_index: number;
  displayed_steps: Section[];
  memory_usage: string;
}

export const emptyRunData: RunData = {
  current_section: "",
  current_step_index: 0,
  displayed_steps: emptySections,
  memory_usage: "",
};

export interface Table {
  table: readonly GridValidRowModel[];
  name: string;
}

export interface RequestData {
  index: number;
  messages: [];
  section: string;
  status: StepStatus;
}

export interface CalculationMessage {
  level: number;
  msg: string;
  trace: string;
}

export interface SwitchComponent {
  name: string;
  value: React.ReactNode;
}
