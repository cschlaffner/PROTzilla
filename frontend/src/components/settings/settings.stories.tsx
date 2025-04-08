import { SettingsProps } from "./settings.props.ts";
import { Settings } from "./settings.tsx";

export default {
  component: Settings,
  title: "Settings",
  argTypes: {},
};

export const standard = (args: SettingsProps): React.ReactNode => (
  <Settings {...args} />
);
standard.args = {
  isOpen: true,
  onClose: () => {
    console.log("Settings closed");
  },
};
