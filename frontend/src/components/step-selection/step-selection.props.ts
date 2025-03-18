import { SectionModes } from "./section-modes.tsx";

export interface StepSelectionProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  runName: string; // Name of the run to which the steps will be added
  section: SectionModes; // Section of the step list to display
  isSmallButton: boolean; // Whether the open button is circular small or with text
}
