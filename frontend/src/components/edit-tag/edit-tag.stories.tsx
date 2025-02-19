import React from "react";

import { EditTag } from "./edit-tag";
import { EditTagProps } from "./edit-tag.props";

export default {
  component: EditTag,
  title: "Edit Tag",
};

export const primary = (args: EditTagProps): React.ReactNode => (
  <EditTag {...args} />
);
primary.args = {
  text: "tag",
  icon: "add",
};
