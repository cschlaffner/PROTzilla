import React from "react";

import { NavbarProps } from "./navbar.props.ts";
import { Navbar } from "./navbar.tsx";

export default {
  component: Navbar,
  title: "Navbar",
  argTypes: {
    onNavigateHome: { action: "back" },
    onOpenMenu: { action: "menu" },
  },
};

export const primary = (args: NavbarProps): React.ReactNode => (
  <Navbar {...args} />
);
primary.args = {
  isDetailsPage: false,
};

export const details = (args: NavbarProps): React.ReactNode => (
  <Navbar {...args} />
);
details.args = {
  title: "my_favorite_run",
  isDetailsPage: true,
};
