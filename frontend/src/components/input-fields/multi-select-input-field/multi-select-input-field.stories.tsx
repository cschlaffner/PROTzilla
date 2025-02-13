import { Meta, StoryFn } from "@storybook/react";
import { MultiSelectInputField } from "./multi-select-input-field";
import { MultiSelectInputFieldProps } from "./multi-select-input-field.props";

export default {
  component: MultiSelectInputField,
  title: "Input Fields / Multi Select Input Field",
  argTypes: { onChange: { action: "changed" } },
} as Meta<MultiSelectInputFieldProps>;

const Template: StoryFn<MultiSelectInputFieldProps> = (args) => {
  return <MultiSelectInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Click and choose Elements",
  options: [
    { label: "Blue", value: "blue" },
    { label: "Red", value: "red" },
    { label: "Orange", value: "orange" },
    { label: "Green", value: "green" },
    { label: "Yellow", value: "yellow" },
  ],
};
