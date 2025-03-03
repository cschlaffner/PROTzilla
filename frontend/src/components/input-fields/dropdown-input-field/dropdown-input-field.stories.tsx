import { Meta, StoryFn } from "@storybook/react";

import { DropdownInputField } from "./dropdown-input-field";
import { DropdownInputFieldProps } from "./dropdown-input-field.props";

export default {
  component: DropdownInputField,
  title: "Input Fields / Dropdown Input Field",
  argTypes: { onChange: { action: "changed" } },
} as Meta<DropdownInputFieldProps>;

const Template: StoryFn<DropdownInputFieldProps> = (args) => {
  return <DropdownInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Choose something",
  options: [
    { label: "Apple", value: "apple" },
    { label: "Banana", value: "banana" },
    { label: "Cherry", value: "cherry" },
    { label: "Date", value: "date" },
    { label: "Grapes", value: "grapes" },
  ],
  defaultOption: "cherry"
};
