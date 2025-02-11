import { Meta, StoryFn } from "@storybook/react";
import { DropdownInputField } from "./dropdown-input-field";
import { DropdownInputFieldProps } from "./dropdown-input-field.props";

export default {
  component: DropdownInputField,
  title: "Input Fields / Dropdown Input Field",
} as Meta<DropdownInputFieldProps>;

const Template: StoryFn<DropdownInputFieldProps> = (args) => {
  return (
    <div>
      <DropdownInputField {...args} />;
    </div>
  );
};

export const primary = Template.bind({});
primary.args = {
  label: "Choose something",
  options: ["Apple", "Banana", "Cherry", "Date", "Grapes"],
};
