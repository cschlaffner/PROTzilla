import { Meta, StoryFn } from "@storybook/react";

import { NumberInputField } from "./number-input-field";
import { NumberInputFieldProps } from "./number-input-field.props";

export default {
  component: NumberInputField,
  title: "Form Components / Number Input Field",
  argTypes: { onChange: { action: "changed" } },
} as Meta<NumberInputFieldProps>;

const Template: StoryFn<NumberInputFieldProps> = (args) => {
  return <NumberInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Your Number",
  value: 5,
  placeholder: "Enter a number",
};

export const steppingMinMax = Template.bind({});
steppingMinMax.args = {
  label: "Your Number",
  value: 5,
  placeholder: "Enter a number",
  min: 1,
  max: 10,
  step: 0.5,
};

export const unit = Template.bind({});
unit.args = {
  label: "Percentage",
  placeholder: "Enter percentage",
  value: 31,
  min: 0,
  max: 100,
  step: 5,
  separatePrefix: "%",
  isInteger: true,
};

export const withStepButtons = Template.bind({});
withStepButtons.args = {
  label: "Font size",
  value: 5,
  step: 1,
  min: 1,
  max: 100,
  hasStepButtons: true,
  separateSuffix: "pt",
  isInteger: true,
};
