import {
  Sections,
  SelectedStep,
  SetSelectedStep,
  StepStatus,
} from "../../types";

export interface SidebarStepProps extends React.HTMLAttributes<HTMLDivElement> {
  number: string;
  name: string;
  stepStatus: StepStatus;
  isCollapsed: boolean;
  sectionName: Sections;
  sectionLength: number;
  index: number;
  selectedStep: SelectedStep | undefined;
  setSelectedStep: SetSelectedStep;
  deleteStep: (index: number) => void;
  setHandlePosition: React.Dispatch<
    React.SetStateAction<{ top: number; left: number }>
  >;
  setShowHandle: React.Dispatch<React.SetStateAction<boolean>>;
  setHoveredStepIndex: React.Dispatch<React.SetStateAction<number>>;
}
