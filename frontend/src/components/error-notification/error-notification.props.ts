import { I18nDescriptionProps, I18nTitleProps } from "../types";

export interface ErrorNotificationProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, "title">,
    I18nTitleProps,
    I18nDescriptionProps {
  /** Indicates if the notification should be shown. */
  isShown?: boolean;

  /** Fires when the notification is manually dismissed. */
  onClose?: () => void;
}
