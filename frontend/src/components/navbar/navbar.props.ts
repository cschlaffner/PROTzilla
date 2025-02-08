import { IconType } from "../icon";
import { I18nTitleProps } from "../types";

export interface NavbarProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title">,
    I18nTitleProps {
  iconCenterRight?: IconType;
  iconHome: IconType;
  iconBurgerMenu: IconType;
}