export interface NavbarProps extends Omit<React.HTMLAttributes<HTMLElement>, "title"> {
  title?: string;
  memoryUsage?: string;
  onNavigateHome: () => void;
  onOpenHelp: () => void;
  showRunInformation: boolean;
}
