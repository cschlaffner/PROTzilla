import { RunData } from "@protzilla/utils";

import { Sections, SelectedStep, Step } from "../types";

export interface SidebarSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  name: Sections;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  currentSteps: Step[];
  setCurrentSteps: (updater: (prevSteps: Step[]) => Step[]) => void;
  stepSectionIndex: number | undefined;
  handleStepSelection: (selectedStep: SelectedStep | undefined) => void;
  runData: RunData;
}
