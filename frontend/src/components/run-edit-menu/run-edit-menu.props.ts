export interface RunEditMenuProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  runName: string;
  onChangeRunName: (newRunName: string) => void;
  ref?: React.Ref<HTMLDivElement>;
}
