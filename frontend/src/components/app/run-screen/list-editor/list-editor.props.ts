import { RunData, SelectedStep } from "@protzilla/utils";

export interface ListEditorProps {
  onFormSubmit: () => void;
  runName: string;
  handleStepSelection: (selectedStep?: SelectedStep | undefined) => void;
  runData: RunData;
}
