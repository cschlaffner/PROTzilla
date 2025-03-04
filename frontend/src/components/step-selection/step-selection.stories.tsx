import { StepSelectionProps } from "./step-selection.props.ts";
import { StepSelection } from "./step-selection.tsx";

export default {
  component: StepSelection,
  title: "StepSelection",
  argTypes: {
    onClose: { action: "close" },
  },
};

const addStepToWorkflow = (step: string) => {
  console.log("Step added to workflow:", step);
};

export const firstTry = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} addStepToWorkflow={addStepToWorkflow} />
);
firstTry.args = {
  isOpen: true,
};
