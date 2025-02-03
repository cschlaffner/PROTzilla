import React from "react";

import { Node } from "./node";
import { NodeProps } from "./node.props";

export default {
  component: Node,
  title: "Node",
};

export const primary = (args: NodeProps): React.ReactNode => <Node {...args} />;
primary.args = {
  title: "Node",
  inputSockets: [{id:0, titleTx:"meep"}]
};
