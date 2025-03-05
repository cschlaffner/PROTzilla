import { SectionNames, SelectedStep, SetSelectedStep } from "../../types";

export interface SidebarStepProps extends React.HTMLAttributes<HTMLDivElement>{
    number:string;
    name:string;
    isCollapsed:boolean;
    sectionName: SectionNames
    index: number;
    selectedStep:SelectedStep;
    setSelectedStep: SetSelectedStep;
    deleteStep: (index:number) => void;
}