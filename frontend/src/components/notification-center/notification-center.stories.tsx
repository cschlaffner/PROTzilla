import { Meta, StoryFn } from "@storybook/react";
import { useTheme } from "styled-components";

import { NotificationCenter } from "./notification-center";
import { ScreenNotification } from "./screen-notification";
import { useNotification } from "./use-notification";
import { SecondaryButton } from "../button";

export default {
  title: "Notification Center",
  component: ScreenNotification,
  argTypes: { onClose: { action: "close" } },
  decorators: [
    (Story) => (
      <NotificationCenter>
        <Story />
      </NotificationCenter>
    ),
  ],
} as Meta;

export const TriggerFromHook: StoryFn = () => {
  const notify = useNotification();
  const theme = useTheme();

  return (
    <div style={{ display: "flex", gap: "1rem", flexDirection: "column" }}>
      <SecondaryButton
        onClick={() => {
          notify({
            title: "Info",
            message:
              "This Notification will close automatically after 10 seconds",
            type: "info",
            closeAfterMs: theme.durations.longNotificationDuration,
          });
        }}
      >
        Info-Notification
      </SecondaryButton>
      <SecondaryButton
        onClick={() => {
          notify({
            title: "Error",
            message: "This Notification can only be closed manually",
            type: "error",
            isClosingAutomatically: false,
          });
        }}
      >
        Error-Notification
      </SecondaryButton>
      <SecondaryButton
        onClick={() => {
          notify({
            title: "Warning",
            message:
              "This Notification will close automatically after 5 seconds",
            type: "warning",
          });
        }}
      >
        Warning-Notification
      </SecondaryButton>
      <SecondaryButton
        onClick={() => {
          notify({
            title: "Success",
            message:
              "Congratulation \n This Notification will close automatically after 2 seconds",
            type: "success",
            closeAfterMs: theme.durations.shortNotificationDuration,
          });
        }}
      >
        Sucess-Notification
      </SecondaryButton>
    </div>
  );
};
