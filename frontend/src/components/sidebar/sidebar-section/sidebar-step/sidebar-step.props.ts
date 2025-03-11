import { SectionNames, SelectedStep, SetSelectedStep } from "../../types";

export interface SidebarStepProps extends React.HTMLAttributes<HTMLDivElement>{
    number: string;
    name: string;
    isCollapsed: boolean;
    sectionName: SectionNames;
    sectionLength: number;
    index: number;
    selectedStep: SelectedStep;
    setSelectedStep: SetSelectedStep;
    deleteStep: (index: number) => void;
    setHandlePosition: any;
    setIsStepHovered:any;
    setHoveredStepIndex:any;
}