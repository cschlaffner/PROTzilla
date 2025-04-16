import { IconType } from "../icon";

export interface TagListProps {
  runName: string;
  tags: string[];
  icon: IconType;
  handleTag: (tag: string, _runName: string) => void;
}
