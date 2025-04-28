import { Section, SelectedStep, Step } from "./types";
import { RunData } from "../../utils";

export interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  runName: string;
  runData: RunData;
  sections: Section[];
  setCurrentSteps: (i: number, updater: (prevSteps: Step[]) => Step[]) => void;
  stepSectionIndex: number | undefined;
  handleStepSelection: (selectedStep: SelectedStep | undefined) => void;
}
