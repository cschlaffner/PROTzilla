import { Meta, StoryFn } from "@storybook/react";
import { useTheme } from "styled-components";

import { NotificationCenter } from "./notification-center";
import { useNotification } from "./use-notification";
import { SecondaryButton } from "../button";

export default {
  title: "Notification Center",
  component: NotificationCenter,
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
            message: "This Notification will close automatically after 5 seconds",
            type: "info",
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
            message: "This Notification will close automatically after 10 seconds",
            type: "warning",
            closeAfterMs: theme.durations.longNotificationDuration,
          });
        }}
      >
        Warning-Notification
      </SecondaryButton>
      <SecondaryButton
        onClick={() => {
          notify({
            title: "Success",
            message: "Congratulation \n This Notification will close automatically after 2 seconds",
            type: "success",
            closeAfterMs: theme.durations.shortNotificationDuration,
          });
        }}
      >
        Sucess-Notification
      </SecondaryButton>
      <SecondaryButton
        onClick={() => {
          notify({
            title: "Oh oh.",
            message:
              "Seems to be a serious issue. \n This notification has a collapsible traceback for even more information.",
            traceback:
              "This is a traceback... A very very very very very very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very very very very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very veryvery very very very long traceback. ",
            type: "error",
            closeAfterMs: theme.durations.veryLongNotificationDuration,
          });
        }}
      >
        Traceback-Notification
      </SecondaryButton>
    </div>
  );
};
