import { Meta, StoryFn } from "@storybook/react";
import { FormProps } from "./form.props"; 
import { Form } from "./form";

export default {
  component: Form,
  title: "Forms / Form",
  argTypes: { onChange: { action: "changed" } },
} as Meta<FormProps>;

const Template: StoryFn<FormProps> = (args) => {
  return <Form {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  formData: {
    label: "Formular Demo",
    onChange: "handleFormChange",
    confirm: true,
    input_fields: [
      {
        type: "text",
        id: "username",
        props: {
          label: "Benutzername",
          defaultValues: "MaxMustermann",
        },
      },
      {
        type: "number",
        id: "age",
        props: {
          label: "Alter",
          defaultValues: 25,
        },
      },
    ],
  },
};
