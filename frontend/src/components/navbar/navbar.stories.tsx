import React from "react";

import { NavbarProps } from "./navbar.props.ts";
import { Navbar } from "./navbar.tsx";

export default {
  component: Navbar,
  title: "Navbar",
  argTypes: {
    onNavigateHome: { action: "back" },
    onOpenHelp: { action: "open help" },
  },
};

export const runOverview = (args: NavbarProps): React.ReactNode => (
  <Navbar {...args} />
);
runOverview.args = {
  allowRunEdit: false,
};

export const details = (args: NavbarProps): React.ReactNode => (
  <Navbar {...args} />
);
details.args = {
  title: "my_favorite_run",
  allowRunEdit: true,
};
