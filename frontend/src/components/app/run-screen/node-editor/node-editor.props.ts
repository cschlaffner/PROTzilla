import { RunData, StepIID } from "@protzilla/utils";

export interface NodeEditorProps {
  onFormSubmit: () => void;
  runName: string;
  navigateOrRefreshSteps: (stepIID?: StepIID) => void;
  runData: RunData;
}
