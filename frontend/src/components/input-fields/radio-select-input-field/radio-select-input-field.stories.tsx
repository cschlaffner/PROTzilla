import { Meta, StoryFn } from "@storybook/react";
import { RadioSelectInputField } from "./radio-select-input-field";
import { RadioSelectInputFieldProps } from "./radio-select-input-field.props";
import { useState } from "react";


export default {
    component: RadioSelectInputField,
    title: "Input Fields / Radio Select Input Field",
  } as Meta<RadioSelectInputFieldProps>;
  
  const Template: StoryFn<RadioSelectInputFieldProps> = (args) => {
    const [selectedValue, setSelectedValue] = useState<string>(args.selectedValue ?? "");
  
    return <RadioSelectInputField {...args} selectedValue={selectedValue} onChange={setSelectedValue} />;
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
    selectedValue: "orange",
};
  