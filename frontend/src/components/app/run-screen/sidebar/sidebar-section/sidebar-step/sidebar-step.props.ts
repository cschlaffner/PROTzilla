import { SectionIDs, SelectedStep, StepStatus } from "@protzilla/utils";

export interface SidebarStepProps extends React.HTMLAttributes<HTMLDivElement> {
  number: string;
  name: string;
  stepStatus: StepStatus;
  isCollapsed: boolean;
  sectionName: SectionIDs;
  sectionLength: number;
  index: number;
  isSelected: boolean;
  navigateOrRefreshSteps: (selectedStep?: SelectedStep | undefined) => void;
  deleteStep: (index: number) => void;
  setHandlePosition: React.Dispatch<React.SetStateAction<{ top: number; left: number }>>;
  setShowHandle: React.Dispatch<React.SetStateAction<boolean>>;
  setHoveredStepIndex: React.Dispatch<React.SetStateAction<number>>;
}
