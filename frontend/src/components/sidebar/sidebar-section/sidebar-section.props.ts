import { Sections, SelectedStep, SetSelectedStep } from "../types";

export interface SidebarSectionProps
  extends React.HTMLAttributes<HTMLDivElement> {
  name: Sections;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  selectedStep: SelectedStep | null;
  setSelectedStep: SetSelectedStep;
  steps: any; //eslint-disable-line
}
