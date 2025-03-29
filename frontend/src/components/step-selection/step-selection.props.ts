import { Sections } from "../sidebar/types.ts";

export interface StepSelectionProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  runName: string; // Name of the run to which the steps will be added
  section: Sections; // Section of the step list to display
  //NOT IMPLEMENTED IN BACKEND YET -
  index: number; // Index in the section for the step to be added to, defaults to last in index
  isSmallButton: boolean; // Whether the open button is circular small or with text
  handlePosition: { top: number; left: number }; // Position of the handle
  onAddStep: () => void; // Function to add a step to the run
  setShowHandle: React.Dispatch<React.SetStateAction<boolean>>;
}
