import { Meta, StoryFn } from "@storybook/react";
import { CheckboxSelectInputField } from "./chechbox-select-input-field";
import { CheckboxSelectInputFieldProps } from "./checkbox-select-input-field.props";
import { useState } from "react";


export default {
    component: CheckboxSelectInputField,
    title: "Input Fields / Checkbox Select Input Field",
  } as Meta<CheckboxSelectInputFieldProps>;
  
  const Template: StoryFn<CheckboxSelectInputFieldProps> = (args) => {
    const [selectedValues, setSelectedValues] = useState<string[]>(args.selectedValues ?? []);
  
    return <CheckboxSelectInputField {...args} selectedValues={selectedValues} onChange={setSelectedValues} />;
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
    selectedValues: ["orange"],
};
  