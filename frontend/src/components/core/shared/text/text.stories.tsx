import { H1, H2, H3, H4, H5, H6, InputLabel, Link, SmallText, Text } from "./text";
import type { LinkProps, TextProps } from "./text.props";

export default {
  component: Text,
  title: "Text",
};

export const primary = (args: TextProps): React.ReactNode => <Text {...args} />;
primary.args = {
  text: "This is an example text.",
};

export const smallText = (args: TextProps): React.ReactNode => <SmallText {...args} />;
smallText.args = {
  text: "This is a small example text.",
};

export const link = (args: LinkProps): React.ReactNode => <Link {...args} />;
link.args = {
  text: "This is a Link",
  href: "https://example.com",
  isDisabled: false,
};

export const h1 = (args: TextProps): React.ReactNode => <H1 {...args} />;
h1.args = {
  text: "This is an H1 title",
};

export const h2 = (args: TextProps): React.ReactNode => <H2 {...args} />;
h2.args = {
  text: "This is an H2 title",
};

export const h3 = (args: TextProps): React.ReactNode => <H3 {...args} />;
h3.args = {
  text: "This is an H3 title",
};

export const h4 = (args: TextProps): React.ReactNode => <H4 {...args} />;
h4.args = {
  text: "This is an H4 title",
};

export const h5 = (args: TextProps): React.ReactNode => <H5 {...args} />;
h5.args = {
  text: "This is an H5 title",
};

export const h6 = (args: TextProps): React.ReactNode => <H6 {...args} />;
h6.args = {
  text: "This is an H6 title",
};

export const inputLabel = (args: TextProps): React.ReactNode => <InputLabel {...args} />;
inputLabel.args = {
  text: "This is an input label",
};
