import { HTMLAttributes, Ref } from "react";

export interface SideMenuProps extends HTMLAttributes<HTMLDivElement> {
  isMenuOpen: boolean;
  ref?: Ref<HTMLDivElement>;
}
