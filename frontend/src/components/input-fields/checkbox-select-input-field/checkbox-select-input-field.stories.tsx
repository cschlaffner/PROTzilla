import { Meta, StoryFn } from "@storybook/react";

import { CheckboxSelectInputField } from "./checkbox-select-input-field.tsx";
import { CheckboxSelectInputFieldProps } from "./checkbox-select-input-field.props";

export default {
  component: CheckboxSelectInputField,
  title: "Input Fields / Checkbox Select Input Field",
  argTypes: { onChange: { action: "changed" } },
} as Meta<CheckboxSelectInputFieldProps>;

const Template: StoryFn<CheckboxSelectInputFieldProps> = (args) => {
  return <CheckboxSelectInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Choose a color",
  options: [
    { label: "Blue", value: "blue" },
    { label: "Red", value: "red" },
    { label: "Orange", value: "orange" },
    { label: "Green", value: "green" },
    { label: "Yellow", value: "yellow" },
  ],
  value: ["orange"],
};
