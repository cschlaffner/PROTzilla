import { Meta, StoryFn } from "@storybook/react";
import { useState } from "react";

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

const StateTemplate: StoryFn<NumberInputFieldProps> = (args) => {
  const [val, setVal] = useState(args.value ?? 0);

  return (
    <NumberInputField
      {...args}
      value={val}
      onChange={(newVal) => {
        setVal(newVal);
        args.onChange(newVal);
      }}
    />
  );
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

export const withStepButtons = StateTemplate.bind({});
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

export const floatField = StateTemplate.bind({});
floatField.args = {
  label: "Percentage",
  value: 0.1,
  step: 0.1,
  min: 0,
  max: 1,
  hasStepButtons: true,
  separateSuffix: "%",
  isInteger: false,
};
