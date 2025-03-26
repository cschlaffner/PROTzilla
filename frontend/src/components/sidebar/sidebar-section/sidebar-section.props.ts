import { SectionNames, SelectedStep, SetSelectedStep } from "../types";

export interface SidebarSectionProps
  extends React.HTMLAttributes<HTMLDivElement> {
  name: SectionNames;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  selectedStep: SelectedStep | null;
  setSelectedStep: SetSelectedStep;
  steps: any;
}
