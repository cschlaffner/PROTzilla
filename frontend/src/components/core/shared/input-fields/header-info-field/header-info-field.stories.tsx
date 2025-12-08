import { action } from "@storybook/addon-actions";
import { Meta, StoryFn } from "@storybook/react";

import { HeaderInfoFieldProps } from "./header-info-field.props.ts";
import { TextInputField } from "../text-input-field";
import { HeaderInfoField } from "./header-info-field.tsx";

export default {
  component: HeaderInfoField,
  title: "Form Components / Header Info Field",
  argTypes: {
    label: { control: "text" },
  },
} as Meta<HeaderInfoFieldProps>;

const Template: StoryFn<HeaderInfoFieldProps> = (args) => {
  return <HeaderInfoField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  label: "This is some nice additional info.",
};

export const AboveForm: StoryFn<HeaderInfoFieldProps> = (args) => {
  return (
    <div>
      <HeaderInfoField {...args} />
      <TextInputField onChange={action("text changed")} label="First name" />
      <TextInputField onChange={action("text changed")} label="Last name" />
    </div>
  );
};
AboveForm.args = {
  label: "Header Info Field",
};
