import { SectionIDs } from "@protzilla/utils";

export interface StepSelectionProps extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  runName: string; // Name of the run to which the steps will be added
  section: SectionIDs; // Section of the step list to display
  onAddStep: () => void; // Function to add a step to the run
  isSmallButton?: boolean; // Whether the open button is circular small or with text
  handlePosition?: { top: number; left: number }; // Position of the handle
  setShowHandle?: React.Dispatch<React.SetStateAction<boolean>>;
  // optional render prop for custom button
  ModalTrigger?: (openModal: () => void) => React.ReactNode;
}
