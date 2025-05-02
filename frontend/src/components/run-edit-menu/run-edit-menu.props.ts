import React from "react";

export interface RunEditMenuProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  runName: string;
  onChangeRunName: (newRunName: string) => void;
  handleAddTag: (tag: string) => void;
  handleDeleteTag: (tagToDelete: string) => void;
  handleToggleFavourite: () => void;
  isOpen: boolean;
  onClose: () => void;
  ref?: React.Ref<HTMLDivElement>;
}
