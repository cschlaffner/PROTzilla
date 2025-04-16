import { SelectedStep } from "./types";

export interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  runName: string;
  runData: any;
  sections: any;
  setCurrentSteps: any;
  stepSectionIndex: number | undefined;
  handleStepSelection: (selectedStep: SelectedStep | undefined) => void;
}
