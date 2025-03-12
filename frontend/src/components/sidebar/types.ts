export type SectionNames =
  | "importing"
  | "data_preprocessing"
  | "data_analysis"
  | "data_integration";
export interface SelectedStep {
  section: SectionNames;
  index: number;
}
export type SetSelectedStep = React.Dispatch<
  React.SetStateAction<SelectedStep>
>;
