export interface StepSelectionProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  runName: string;
  onClose: () => void;
  addStepToWorkflow: (step: string) => void;
}
