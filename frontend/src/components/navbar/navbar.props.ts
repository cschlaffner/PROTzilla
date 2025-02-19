import { I18nTitleProps } from "../types";

export interface NavbarProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title">,
    I18nTitleProps {
  onNavigateHome: () => void;
  isDetailsPage: boolean;
}
