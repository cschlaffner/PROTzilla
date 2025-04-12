import { action } from "@storybook/addon-actions";
import { Meta, StoryFn } from "@storybook/react";

import { FormDivider } from "./form-divider";
import { FormDividerProps } from "./form-divider.props";
import { TextInputField } from "../text-input-field";

export default {
  component: FormDivider,
  title: "Input Fields / Form Divider",
  argTypes: {
    label: { control: "text" },
  },
} as Meta<FormDividerProps>;

const Template: StoryFn<FormDividerProps> = (args) => {
  return <FormDivider {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "Let`s divide some stuff",
};

export const WithinForm: StoryFn<FormDividerProps> = (args) => {
  return (
    <div>
      <TextInputField onChange={action("text changed")} label="First name" />
      <FormDivider {...args} />
      <TextInputField onChange={action("text changed")} label="First name" />
    </div>
  );
};
WithinForm.args = {
  label: "Section Divider",
};
