import { Sections, Step } from "../types";

export interface SidebarSectionProps
  extends React.HTMLAttributes<HTMLDivElement> {
  name: Sections;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  stepSectionIndex: number | undefined;
  handleStepSelection: any;
  runData: any;
  steps: Step[];
}
