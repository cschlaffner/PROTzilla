import { action } from "@storybook/addon-actions";
import { Meta, StoryFn } from "@storybook/react";

import { InfoFieldProps } from "./info-field.props.ts";
import { InfoField } from "./info-field.tsx";
import { TextInputField } from "../text-input-field";

export default {
  component: InfoField,
  title: "Form Components / Info Field",
  argTypes: {
    label: { control: "text" },
  },
} as Meta<InfoFieldProps>;

const Template: StoryFn<InfoFieldProps> = (args) => {
  return <InfoField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "This is some nice additional info.",
};

export const WithinForm: StoryFn<InfoFieldProps> = (args) => {
  return (
    <div>
      <TextInputField onChange={action("text changed")} label="First name" />
      <InfoField {...args} />
      <TextInputField onChange={action("text changed")} label="First name" />
    </div>
  );
};
WithinForm.args = {
  label: "Info Field",
};
