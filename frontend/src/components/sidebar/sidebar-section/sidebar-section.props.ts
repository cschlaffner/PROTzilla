import { SectionNames, SelectedStep, SetSelectedStep } from "../types";

export interface SidebarSectionProps
  extends React.HTMLAttributes<HTMLDivElement> {
  name: SectionNames;
  index: number;
  title: string;
  isCollapsed: boolean;
  selectedStep: SelectedStep;
  setSelectedStep: SetSelectedStep;
}
