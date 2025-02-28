import { Meta, StoryFn } from "@storybook/react";

import { FileInputField } from "./file-input-field";
import { FileInputFieldProps } from "./file-input-field.props";

export default {
  component: FileInputField,
  title: "Input Fields / File Input Field",
  argTypes: { onChange: { action: "changed" } },
} as Meta<FileInputFieldProps>;

const Template: StoryFn<FileInputFieldProps> = (args) => {
  return <FileInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Funny data file",
};

export const allAffix = Template.bind({});
allAffix.args = {
  label: "Your Input",
  inlinePrefix: "%",
  inlineSuffix: "%",
  separatePrefix: "%",
  separateSuffix: "%",
};
