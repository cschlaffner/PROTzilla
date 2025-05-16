import { Sections } from "@protzilla/utils";

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
  section: Sections.Importing,
  isSmallButton: true,
  index: 0,
  handlePosition: { top: 400, left: 600 },
};

export const dataAnalysisSteps = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
dataAnalysisSteps.args = {
  runName: "runrun",
  section: Sections.DataAnalysis,
  isSmallButton: true,
  index: 0,
  handlePosition: { top: 400, left: 600 },
};

export const dataIntegrationSteps = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
dataIntegrationSteps.args = {
  runName: "runrun",
  section: Sections.DataIntegration,
  isSmallButton: true,
  index: 0,
  handlePosition: { top: 400, left: 600 },
};

export const dataPreprocessingSteps = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
dataPreprocessingSteps.args = {
  runName: "runrun",
  section: Sections.DataPreprocessing,
  isSmallButton: true,
  index: 0,
  handlePosition: { top: 400, left: 600 },
};

export const withBiggerButton = (args: StepSelectionProps): React.ReactNode => (
  <StepSelection {...args} />
);
withBiggerButton.args = {
  runName: "runrun",
  section: Sections.DataPreprocessing,
  isSmallButton: false,
  index: 0,
  handlePosition: { top: 0, left: 0 },
};
