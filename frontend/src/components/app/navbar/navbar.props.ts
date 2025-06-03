export interface NavbarProps extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  title?: string;
  memoryUsage?: string;
  onNavigateHome: () => void;
  onOpenSettings: () => void;
  onOpenHelp: () => void;
  showRunInformation: boolean;
}
