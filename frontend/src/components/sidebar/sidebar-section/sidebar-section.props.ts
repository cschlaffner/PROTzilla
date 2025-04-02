import { Sections, SelectedStep, SetSelectedStep, Step } from "../types";

export interface SidebarSectionProps
  extends React.HTMLAttributes<HTMLDivElement> {
  name: Sections;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  selectedStep: SelectedStep | undefined;
  setSelectedStep: SetSelectedStep;
  steps: Step[];
}
