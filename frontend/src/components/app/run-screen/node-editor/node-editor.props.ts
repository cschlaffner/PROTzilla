import { RunData, StepID } from "@protzilla/utils";

export interface NodeEditorProps {
  onFormSubmit: () => void;
  runName: string;
  navigateOrRefreshSteps: (stepID?: StepID) => void;
  runData: RunData;
}
