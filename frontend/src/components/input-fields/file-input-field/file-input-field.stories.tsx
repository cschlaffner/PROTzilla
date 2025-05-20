import { Meta, StoryFn } from "@storybook/react";

import { FileInputField } from "./file-input-field";
import { FileInputFieldProps } from "./file-input-field.props";

export default {
  component: FileInputField,
  title: "Form Fields / File Input Field",
  argTypes: {
    placeholder: { control: "text" },
    onChange: { action: "changed" },
    value: { control: { type: "file", accept: "*/*" } },
  },
} as Meta<FileInputFieldProps>;

const Template: StoryFn<FileInputFieldProps> = (args) => {
  return <FileInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Funny data file",
};
