import { useContext } from "react";

import { NotificationContext } from "./notification-context";

export const useNotification = () => {
  const notify = useContext(NotificationContext);
  if (!notify) {
    throw new Error("useNotification must be used within NotificationCenter");
  }
  return notify;
};
