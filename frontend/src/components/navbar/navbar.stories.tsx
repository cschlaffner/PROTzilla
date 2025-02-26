import React from "react";

import { NavbarProps } from "./navbar.props.ts";
import { Navbar } from "./navbar.tsx";

export default {
  component: Navbar,
  title: "Navbar",
  argTypes: {
    onNavigateHome: { action: "back" },
    onOpenSettings: { action: "open settings" },
  },
};

export const runOverview = (args: NavbarProps): React.ReactNode => (
  <Navbar {...args} />
);
runOverview.args = {
  showHomeButton: false,
  allowRunEdit: false,
};

export const details = (args: NavbarProps): React.ReactNode => (
  <Navbar {...args} />
);
details.args = {
  title: "my_favorite_run",
  showHomeButton: true,
  allowRunEdit: true,
};

export const other = (args: NavbarProps): React.ReactNode => (
  <Navbar {...args} />
);
other.args = {
  showHomeButton: true,
  allowRunEdit: false,
};
