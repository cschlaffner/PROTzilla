import React, { createContext, ReactNode, useContext, useState } from "react";
import { styled } from "styled-components";

import {
  spacing,
  zIndex,
} from "../../theme";
import { NotificationProps } from "./notification/notification.props";
import { FlexColumn } from "../box";

const Container = styled(FlexColumn)`
  position: fixed;
  top: 150px;
  right: 150px;
  gap: ${spacing("small")};
  z-index: ${zIndex("notification")};
`;

interface NotificationWithId extends NotificationProps {
  id: string;
}

const NotificationContext = createContext<{
  addNotification: (notification: Omit<NotificationWithId, "id">) => void;
}>({
  addNotification: () => {},
});

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<NotificationWithId[]>([]);

  const addNotification = (notification: Omit<NotificationWithId, "id">) => {
    const id = Math.random().toString(36).substr(2, 9);
    setNotifications((prev) => [...prev, { ...notification, id }]);

    if (notification.closeAfterMs && notification.closeAfterMs > 0) {
      setTimeout(() => removeNotification(id), notification.closeAfterMs);
    }
  };

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      <Container>
        {notifications.map(({ id, ...props }) => (
          <Notification key={id} title="" type="error" {...props} onClose={() => removeNotification(id)} isShown />
        ))}
      </Container>
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => useContext(NotificationContext);
