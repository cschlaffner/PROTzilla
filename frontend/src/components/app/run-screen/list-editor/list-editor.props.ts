import { RunData, SelectedStep } from "@protzilla/utils";

export interface ListEditorProps {
  onFormSubmit: () => void;
  runName: string;
  navigateOrRefreshSteps: (selectedStep?: SelectedStep | undefined) => void;
  runData: RunData;
}
