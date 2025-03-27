import { Run } from "../../utils";

export interface TagListProps {
  run: Run;
  handleDeleteTag: (runName: string, tag: string) => void;
}