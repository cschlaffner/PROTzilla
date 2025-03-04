export interface StepSelectionProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  isOpen: boolean;
  runName: string;
  onClose: () => void;
  addStepToWorkflow: (step: string) => void;
}
