import { SelectedStep } from "../../sidebar/types";

export interface ListEditorProps {
  onFormSubmit: () => void;
  runName: string;
  handleStepSelection: (selectedStep: SelectedStep | undefined) => void;
  runData: any;
}
