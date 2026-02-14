import { RunData, Section, StepIID } from "@protzilla/utils";

export interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  runName: string;
  runData: RunData;
  sections: Section[];
  stepSectionIndex: number | undefined;
  navigateOrRefreshSteps: (stepIID?: StepIID) => void;
}
