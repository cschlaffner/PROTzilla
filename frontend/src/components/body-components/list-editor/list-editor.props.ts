import { FormData, InputValueType } from "../../forms/form";

export interface ListEditorProps {
    formDataParameters: FormData;
    onChangeParamters: (data: Record<string, InputValueType>) => void;
    formDataPlotSettings: FormData;
    onChangePlotSettings: (data: Record<string, InputValueType>) => void;
    runName: string;
}
