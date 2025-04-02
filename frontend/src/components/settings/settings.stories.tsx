import { Settings } from "./settings.tsx";

export default {
  component: Settings,
  title: "Settings",
  argTypes: {},
};

export const standard = (args: any): React.ReactNode => <Settings {...args} />;
standard.args = {
  isOpen: true,
  onClose: () => {},
};
