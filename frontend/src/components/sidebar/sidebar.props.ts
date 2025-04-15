import { SelectedStep } from "./types";

export interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  runName: string;
  runData: any;
  handleStepSelection: (selectedStep: SelectedStep | undefined) => void;
}
