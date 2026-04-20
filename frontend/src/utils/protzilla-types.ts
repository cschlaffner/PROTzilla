import { GridValidRowModel } from "@mui/x-data-grid";
import type { Edge } from "@xyflow/react";

import { CrosslinkerInformation } from "../components/core/shared/molstar-viewer/crosslinker-processing.tsx";

export interface UIStateProps {
  isDisabled?: boolean;
}

export interface SelectedStep {
  section: SectionIDs;
  index: number;
}

export type StepID = string;

export interface StepOutputInfo {
  label: string;
  display_name: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface Image {
  title: string;
  alt: string;
  data: string;
}

export interface Download {
  data: Record<string, unknown>;
}

export interface Visualization {
  structureEntryId: string;
  cifString: string;
  crosslinks?: CrosslinkerInformation[];
}

// We assume these are the only data types we receive for tables
export type TableRecord = Record<string, number | string | null>;

export type StepStatus = "complete" | "outdated" | "incomplete" | "failed";

export interface Step {
  id: string;
  name: string;
  section: SectionIDs;
  input_keys: string[];
  output_keys: string[];
  visual_data?: {
    node_position?: {
      x: number;
      y: number;
    };
  };
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
}

export const supportedSections: Section[] = [
  {
    id: SectionIDs.Importing,
    name: "Importing",
  },
  {
    id: SectionIDs.DataPreprocessing,
    name: "Data Preprocessing",
  },
  {
    id: SectionIDs.DataAnalysis,
    name: "Data Analysis",
  },
  {
    id: SectionIDs.DataIntegration,
    name: "Data Integration",
  },
];

// TODO: remove with List editor refactoring
export const emptySections: Section[] = supportedSections;

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
  current_step_id: StepID;
  displayed_steps: Step[];
  memory_usage: string;
  current_step_has_plot: boolean;
  recommended_next_step_id: StepID;
  graph_edges: Edge[];
}

export const emptyRunData: RunData = {
  current_section: "",
  current_step_id: "",
  displayed_steps: [],
  memory_usage: "",
  current_step_has_plot: false,
  recommended_next_step_id: "",
  graph_edges: [],
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
