import { StepSelectionProps } from "./step-selection.props.ts";
import { SectionModes, StepSelection } from "./step-selection.tsx";

export default {
  component: StepSelection,
  title: "StepSelection",
  argTypes: {},
};

export const viaAddButton = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
viaAddButton.args = {
  runName: "runrun",
  section: SectionModes.Importing,
};
