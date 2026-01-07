import { RunData, SelectedStep } from "@protzilla/utils";

export interface NodeEditorProps {
  onFormSubmit: () => void;
  runName: string;
  navigateOrRefreshSteps: (selectedStep?: SelectedStep) => void;
  runData: RunData;
}
