import { Navbar } from "./navbar.tsx";
import { NavbarProps } from "./navbar.props.ts";
import React from "react";

export default {
  component: Navbar,
  title: "Navbar",
};

export const primary = (args: NavbarProps): React.ReactNode => <Navbar {...args} />;
primary.args = {
  title: "Protzilla",
  iconCenterRight: "add",
  iconHome: "eye",
  iconBurgerMenu: "burgerMenu",
  tags: ""
};