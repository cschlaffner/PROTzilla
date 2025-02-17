import { Meta, StoryFn } from "@storybook/react";

import { NumberInputField } from "./number-input-field";
import { NumberInputFieldProps } from "./number-input-field.props";

export default {
  component: NumberInputField,
  title: "Input Fields / Number Input Field",
  argTypes: { onChange: { action: "changed" } },
} as Meta<NumberInputFieldProps>;

const Template: StoryFn<NumberInputFieldProps> = (args) => {
  return <NumberInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Your Number",
  defaultValue: 5,
  placeholder: "Enter a number",
};

export const steppingMinMax = Template.bind({});
steppingMinMax.args = {
  label: "Your Number",
  defaultValue: 5,
  placeholder: "Enter a number",
  min: 1,
  max: 10,
  step: 0.5,
};

export const unit = Template.bind({});
unit.args = {
  label: "Percentage",
  placeholder: "Enter percentage",
  defaultValue: 31,
  min: 0,
  max: 100,
  step: 5,
  separatePrefix: "%",
};
