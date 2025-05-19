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

export const small = (args: IconProps): React.ReactNode => <Icon {...args} />;
small.args = {
  icon: "add",
  isSmall: true,
};

export const big = (args: IconProps): React.ReactNode => <Icon {...args} />;
big.args = {
  icon: "add",
  isBig: true,
};
