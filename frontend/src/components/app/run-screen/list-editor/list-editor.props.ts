import { RunData, StepID } from "@protzilla/utils";

export interface ListEditorProps {
  onFormSubmit: () => void;
  runName: string;
  navigateOrRefreshSteps: (stepID?: StepID) => void;
  runData: RunData;
}
