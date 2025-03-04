export interface StepSelectionProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  isOpen: boolean;
  onClose: () => void;
  addStepToWorkflow: (step: string) => void;
}
