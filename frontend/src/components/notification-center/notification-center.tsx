import React, { useCallback, useState } from "react";
import { styled } from "styled-components";
import { v4 as uuidv4 } from "uuid";

import { NotificationContext } from "./notification-context";
import { ScreenNotification } from "./screen-notification";
import { ScreenNotificationProps } from "./screen-notification/screen-notification.props";
import { spacing, zIndex } from "../../theme";

type NotificationItem = ScreenNotificationProps & { id: string };

const NotificationStack = styled.div`
  position: fixed;
  top: calc(${spacing("large")} + ${spacing("navbarHeight")});
  right: ${spacing("large")};
  display: flex;
  flex-direction: column;
  gap: ${spacing("small")};
  z-index: ${zIndex("notification")};
  width: 25vw;
`;

export const NotificationCenter: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const notify = useCallback(
    (notification: Omit<ScreenNotificationProps, "isShown">) => {
      const id = uuidv4();
      const newNotification: NotificationItem = {
        ...notification,
        id,
        isShown: true,
        onClose: () => {
          setNotifications((prev) => prev.filter((n) => n.id !== id));
          notification.onClose?.();
        },
      };

      setNotifications((prev) => [...prev, newNotification]);
    },
    [],
  );

  return (
    <NotificationContext.Provider value={notify}>
      {children}
      <NotificationStack>
        {notifications.map((n) => (
          <ScreenNotification key={n.id} {...n} />
        ))}
      </NotificationStack>
    </NotificationContext.Provider>
  );
};
