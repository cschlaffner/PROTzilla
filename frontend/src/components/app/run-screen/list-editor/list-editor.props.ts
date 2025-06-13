import { RunData, SelectedStep } from "@protzilla/utils";

export interface ListEditorProps {
  onFormSubmit: () => void;
  runName: string;
  navigateOrRefreshSteps: (selectedStep?: SelectedStep) => void;
  runData: RunData;
}
