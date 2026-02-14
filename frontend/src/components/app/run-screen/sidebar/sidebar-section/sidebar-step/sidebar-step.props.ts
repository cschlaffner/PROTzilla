import { SectionIDs, StepIID, StepStatus } from "@protzilla/utils";

export interface SidebarStepProps extends React.HTMLAttributes<HTMLDivElement> {
  number: string;
  name: string;
  stepStatus: StepStatus;
  isCollapsed: boolean;
  sectionName: SectionIDs;
  sectionLength: number;
  index: number;
  iid: StepIID;
  isSelected: boolean;
  navigateOrRefreshSteps: (stepIID: StepIID) => void;
  deleteStep: (stepIID: StepIID) => void;
  setHandlePosition: React.Dispatch<React.SetStateAction<{ top: number; left: number }>>;
  setShowHandle: React.Dispatch<React.SetStateAction<boolean>>;
  setHoveredStepIndex: React.Dispatch<React.SetStateAction<number>>;
}
