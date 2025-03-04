import { StepSelectionProps } from "./step-selection.props.ts";
import { StepSelection } from "./step-selection.tsx";

export default {
  component: StepSelection,
  title: "StepSelection",
  argTypes: {
    onClose: { action: "close" },
  },
};

export const firstTry = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
firstTry.args = {
  isOpen: true,
};
