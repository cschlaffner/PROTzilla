import { Meta, StoryFn } from "@storybook/react";

import { ErrorNotification } from "./error-notification";
import type { ErrorNotificationProps } from "./error-notification.props";

export default {
  title: "ErrorNotification",
  component: ErrorNotification,
  argTypes: { onClose: { action: "close" } },
} as Meta;

export const ActiveError: StoryFn<ErrorNotificationProps> = (args) => (
  <ErrorNotification {...args} />
);
ActiveError.args = {
  isShown: true,
  title: "Fehler",
  description: "Text",
};
