import { SelectedStep } from "./types";

export interface SidebarProps extends React.HTMLAttributes<HTMLDivElement>{
    runName: string;
    handleStepSelection: (selectedStep: SelectedStep | null) => void;
}
