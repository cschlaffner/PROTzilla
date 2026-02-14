import { RunData, SectionIDs, Step, StepIID } from "@protzilla/utils";

export interface SidebarSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  name: SectionIDs;
  runName: string;
  index: number;
  title: string;
  isCollapsed: boolean;
  currentSteps: Step[];
  stepSectionIndex: number | undefined;
  navigateOrRefreshSteps: (stepIID?: StepIID) => void;
  runData: RunData;
}
