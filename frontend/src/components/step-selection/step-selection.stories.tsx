import { StepSelectionProps } from "./step-selection.props.ts";
import { StepSelection } from "./step-selection.tsx";
import { Sections } from "../sidebar/types.ts";

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
  section: Sections.Importing,
  isSmallButton: true,
};

export const dataAnalysisSteps = (
  args: StepSelectionProps,
): React.ReactNode => <StepSelection {...args} />;
dataAnalysisSteps.args = {
  runName: "runrun",
  section: Sections.DataAnalysis,
  isSmallButton: true,
};

export const dataIntegrationSteps = (
  args: StepSelectionProps,
): React.ReactNode => <StepSelection {...args} />;
dataIntegrationSteps.args = {
  runName: "runrun",
  section: Sections.DataIntegration,
  isSmallButton: true,
};

export const dataPreprocessingSteps = (
  args: StepSelectionProps,
): React.ReactNode => <StepSelection {...args} />;
dataPreprocessingSteps.args = {
  runName: "runrun",
  section: Sections.DataPreprocessing,
  isSmallButton: true,
};

export const withBiggerButton = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
withBiggerButton.args = {
  runName: "runrun",
  section: Sections.DataPreprocessing,
  isSmallButton: false,
};
