import { Meta, StoryFn } from "@storybook/react";
import { NumberField } from "./number-field";
import { NumberFieldProps } from "./number-field.props";
import { useState } from "react";


export default {
    title: "Components/NumberField",
    component: NumberField,
} as Meta<NumberFieldProps>;


const Template: Story<any> = (args) => <NumberField {...args} />;

export const Default = Template.bind({});
Default.args = {
  label: "Your Number",
  value: 5,
  placeholder: "Enter a number",
  min: 1,
  max: 10,
  step: 1,
};