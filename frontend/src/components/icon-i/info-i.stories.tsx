import React from "react";

import { InfoIComponent } from "./info-i";
import { InfoIProps } from "./info-i.props";

export default {
  component: InfoIComponent,
  title: "Info I",
};

export const onHover = (args: InfoIProps): React.ReactNode => (
  <InfoIComponent {...args} />
);
onHover.args = {
  text: "Das ist ein Text zur Information!",
};
