export interface NavbarProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  title?: string;
  onNavigateHome: () => void;
  onOpenSettings: () => void;
  onOpenHelp: () => void;
  allowRunEdit: boolean;
}
