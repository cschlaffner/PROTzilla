import { SectionModes } from "./section-modes.tsx";
import { StepSelectionProps } from "./step-selection.props.ts";
import { StepSelection } from "./step-selection.tsx";

export default {
  component: StepSelection,
  title: "StepSelection",
  argTypes: {},
};

export const importingSteps = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
importingSteps.args = {
  runName: "runrun",
  section: SectionModes.Importing,
};

export const dataAnalysisSteps = (
  args: StepSelectionProps,
): React.ReactNode => <StepSelection {...args} />;
dataAnalysisSteps.args = {
  runName: "runrun",
  section: SectionModes.DataAnalysis,
};

export const dataIntegrationSteps = (
  args: StepSelectionProps,
): React.ReactNode => <StepSelection {...args} />;
dataIntegrationSteps.args = {
  runName: "runrun",
  section: SectionModes.DataIntegration,
};

export const dataPreproscessingSteps = (
  args: StepSelectionProps,
): React.ReactNode => <StepSelection {...args} />;
dataPreproscessingSteps.args = {
  runName: "runrun",
  section: SectionModes.DataPreprocessing,
};
