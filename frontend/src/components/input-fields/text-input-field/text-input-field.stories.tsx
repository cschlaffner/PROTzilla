import { Meta, StoryFn } from "@storybook/react";

import { TextInputField } from "./text-input-field";
import { TextInputFieldProps } from "./text-input-field.props";

export default {
  component: TextInputField,
  title: "Input Fields / Text Input Field",
  argTypes: { onChange: { action: "changed" } },
} as Meta<TextInputFieldProps>;

const Template: StoryFn<TextInputFieldProps> = (args) => {
  return <TextInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Your Input",
  placeholder: "Type something",
};

export const allAffix = Template.bind({});
allAffix.args = {
  label: "Your Input",
  placeholder: "Type something",
  inlinePrefix: "%",
  inlineSuffix: "%",
  separatePrefix: "%",
  separateSuffix: "%",
  isSmall: true,
};
