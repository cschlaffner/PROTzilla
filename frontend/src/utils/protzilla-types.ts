import { emptySections, Section, StepStatus } from "../components/sidebar/types.ts";

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

export interface RequestData {
  index: number;
  messages: [];
  section: string;
  status: StepStatus;
}

export interface PlotlyFigure {
  data: Partial<Plotly.Data>[];
  layout: Partial<Plotly.Layout>;
}