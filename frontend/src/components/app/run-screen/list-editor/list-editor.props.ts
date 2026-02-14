import { RunData, StepIID } from "@protzilla/utils";

export interface ListEditorProps {
  onFormSubmit: () => void;
  runName: string;
  navigateOrRefreshSteps: (stepIID?: StepIID) => void;
  runData: RunData;
}
