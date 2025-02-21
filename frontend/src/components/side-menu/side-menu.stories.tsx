import { SideMenuProps } from "./side-menu.props.ts";
import { SideMenu } from "./side-menu.tsx";

export default {
  component: SideMenu,
  title: "Navbar Side-menu",
  argTypes: {
    onOpenSettings: { action: "opening settings" },
    onOpenGithub: { action: "opening github" },
  },
};

export const primary = (args: SideMenuProps): React.ReactNode => (
  <SideMenu {...args} />
);
primary.args = {
  isOpen: true,
};
