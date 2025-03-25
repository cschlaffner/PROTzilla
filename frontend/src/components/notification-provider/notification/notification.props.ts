
export interface NotificationProps{
  title: string;
  message?: string;
  type : 'error' | 'success' | 'warning' | 'info';
  isShown?: boolean;
  closeAfterMs?: number;
  onClose?: () => void;
}
