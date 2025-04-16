import { Sections } from "../types";

export interface SidebarSectionProps
  extends React.HTMLAttributes<HTMLDivElement> {
  name: Sections;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  currentSteps: any;
  setCurrentSteps: any;
  stepSectionIndex: number | undefined;
  handleStepSelection: any;
  runData: any;
}
