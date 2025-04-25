import { SelectedStep } from "../../sidebar/types";

export interface ListEditorProps {
  onFormSubmit: () => void;
  onFormChange: () => void;
  runName: string;
  handleStepSelection: (selectedStep: SelectedStep | undefined) => void;
  runData: any;
}
