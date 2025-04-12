import { Meta } from "@storybook/react";

import { SettingsProps } from "./settings.props.ts";
import { Settings } from "./settings.tsx";
import { NotificationCenter } from "../notification-center";

export default {
  component: Settings,
  title: "Settings",
  argTypes: { onClose: { action: "close" } },
  decorators: [
    (Story) => (
      <NotificationCenter>
        <Story />
      </NotificationCenter>
    ),
  ],
} as Meta;

export const standard = (args: SettingsProps): React.ReactNode => (
  <Settings {...args} />
);
standard.args = {
  isOpen: true,
};
