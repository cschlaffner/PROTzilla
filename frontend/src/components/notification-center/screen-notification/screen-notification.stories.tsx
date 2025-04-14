import { Meta, StoryFn } from "@storybook/react";

import { ScreenNotification } from "./screen-notification";
import type { ScreenNotificationProps } from "./screen-notification.props";

export default {
  title: "Notification (Screen)",
  component: ScreenNotification,
  argTypes: { onClose: { action: "close" } },
} as Meta;

export const ActiveError: StoryFn<ScreenNotificationProps> = (args) => (
  <ScreenNotification {...args} />
);
ActiveError.args = {
  isShown: true,
  title: "Fehler",
  message: "Text",
  type: "error",
  isClosingAutomatically: false,
};
