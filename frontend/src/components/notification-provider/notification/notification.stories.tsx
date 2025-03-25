import { Meta, StoryFn } from "@storybook/react";

import { Notification } from "./notification";
import type { NotificationProps } from "./notification.props";

export default {
  title: "Notification",
  component: Notification,
  argTypes: { onClose: { action: "close" } },
} as Meta;

export const ActiveError: StoryFn<NotificationProps> = (args) => (
  <Notification {...args} />
);
ActiveError.args = {
  isShown: true,
  title: "Fehler",
  message: "Text",
  type: "error",
};
