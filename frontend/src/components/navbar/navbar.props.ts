import { I18nTitleProps } from "../types";

export interface NavbarProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title">,
    I18nTitleProps {
  memoryUsage?: string;
  onNavigateHome: () => void;
  onOpenSettings: () => void;
  onOpenHelp: () => void;
  allowRunEdit: boolean;
}
