import { Icon } from "./icon";
import type { IconProps } from "./icon.props";

export default {
  component: Icon,
  title: "Icon",
};

export const primary = (args: IconProps): React.ReactNode => <Icon {...args} />;
primary.args = {
  icon: "add",
};
