import { createContext } from "react";

import { ScreenNotificationProps } from "./screen-notification/screen-notification.props";

export const NotificationContext = createContext<
  ((notification: Omit<ScreenNotificationProps, "isShown">) => void) | undefined
>(undefined);
