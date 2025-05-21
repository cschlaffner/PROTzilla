export interface ScreenNotificationProps {
  title: string;
  message?: string;
  traceback?: string;
  type: "error" | "success" | "warning" | "info";
  isShown?: boolean;
  isClosingAutomatically?: boolean;
  closeAfterMs?: number;
  onClose?: () => void;
}
