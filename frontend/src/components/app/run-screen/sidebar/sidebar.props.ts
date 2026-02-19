import { RunData, Section, StepID } from "@protzilla/utils";

export interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  runName: string;
  runData: RunData;
  sections: Section[];
  stepSectionIndex: number | undefined;
  navigateOrRefreshSteps: (stepID?: StepID) => void;
}
