import { FormData, InputValueType } from "../../forms/form";
import { SelectedStep } from "../../sidebar/types";

export interface ListEditorProps {
  formDataParameters: FormData;
  onChangeParameters: (data: Record<string, InputValueType>) => void;
  runName: string;
  handleStepSelection: (selectedStep: SelectedStep | undefined) => void;
  onCalculateStep: () => void;
  runData: any;
}
