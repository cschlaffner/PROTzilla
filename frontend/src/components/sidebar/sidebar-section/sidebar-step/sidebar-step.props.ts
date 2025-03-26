import { Sections, SelectedStep, SetSelectedStep } from "../../types";

export interface SidebarStepProps extends React.HTMLAttributes<HTMLDivElement> {
  number: string;
  name: string;
  isCollapsed: boolean;
  sectionName: Sections;
  sectionLength: number;
  index: number;
  selectedStep: SelectedStep | null;
  setSelectedStep: SetSelectedStep;
  deleteStep: (index: number) => void;
  setHandlePosition: React.Dispatch<
    React.SetStateAction<{ top: number; left: number }>
  >;
  setShowHandle: React.Dispatch<React.SetStateAction<boolean>>;
  setHoveredStepIndex: React.Dispatch<React.SetStateAction<number>>;
}
