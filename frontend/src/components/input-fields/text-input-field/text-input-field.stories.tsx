import { Meta, StoryFn } from "@storybook/react";
import { TextInputField } from "./text-input-field";
import { useState } from "react";
import { TextInputFieldProps } from "./text-input-field.props";


export default {
    component: TextInputField,
    title: "Input Fields / Text Input Field",
} as Meta<TextInputFieldProps>;


const Template: StoryFn<TextInputFieldProps> = (args) => {
  const [value, setValue] = useState<string>(args.value ?? "");

  return <TextInputField {...args} value={value} onChange={setValue} />;
};


export const primary = Template.bind({});
primary.args = {
  label: "Your Input",
  value: "",
  placeholder: "Type something",
};