export interface StepSelectionProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  runName: string; // Name of the run to which the steps will be added
}
