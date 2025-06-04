import { RunData, SectionIDs, SelectedStep, Step } from "@protzilla/utils";

export interface SidebarSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  name: SectionIDs;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  currentSteps: Step[];
  stepSectionIndex: number | undefined;
  navigateOrRefreshSteps: (selectedStep?: SelectedStep | undefined) => void;
  runData: RunData;
}
