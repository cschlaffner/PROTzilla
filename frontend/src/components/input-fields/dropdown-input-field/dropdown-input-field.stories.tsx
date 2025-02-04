import { Meta, StoryFn } from "@storybook/react";
import { DropdownInputField } from "./dropdown-input-field";
import { useState } from "react";
import { DropdownInputFieldProps } from "./dropdown-input-field.props";

export default {
  component: DropdownInputField,
  title: "Input Fields / Dropdown Input Field",
} as Meta<DropdownInputFieldProps>;

const Template: StoryFn<DropdownInputFieldProps> = (args) => {
  const [selectedValue, setSelectedValue] = useState<string>(args.value ?? "");

  return (
    <DropdownInputField
      {...args}
      value={selectedValue}
      onSelect={setSelectedValue}
    />
  );
};

export const primary = Template.bind({});
primary.args = {
  label: "Choose something",
  placeholder: "Select an option...",
  options: ["Apple", "Banana", "Cherry", "Date", "Grapes"],
};
