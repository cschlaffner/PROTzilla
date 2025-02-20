import { Meta, StoryFn } from "@storybook/react";

import { Form } from "./form";
import { FormProps } from "./form.props";

export default {
  component: Form,
  title: "Forms / Form",
  argTypes: {
    onChange: { action: "changed" },
    onFormTouched: { action: "form has changed" },
  },
} as Meta<FormProps>;

const Template: StoryFn<FormProps> = (args) => {
  return <Form {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  formData: {
    label: "Formular Demo",
    submit: false,
    input_fields: [
      {
        type: "text",
        id: "username",
        props: {
          label: "Benutzername",
        },
      },
      {
        type: "number",
        id: "age",
        props: {
          label: "Alter",
        },
      },
      {
        type: "multi-select",
        id: "country",
        props: {
          label: "Land",
          options: [
            { label: "Deutschland", value: "DE" },
            { label: "Österreich", value: "AT" },
            { label: "Schweiz", value: "CH" },
            { label: "Frankreich", value: "FR" },
            { label: "Italien", value: "IT" },
          ],
        },
      },
    ],
  },
};

export const submit = Template.bind({});
submit.args = {
  formData: {
    label: "Formular Demo",
    submit: true,
    input_fields: [
      {
        type: "text",
        id: "username",
        props: {
          label: "Benutzername",
        },
      },
      {
        type: "number",
        id: "age",
        props: {
          label: "Alter",
        },
      },
      {
        type: "multi-select",
        id: "country",
        props: {
          label: "Land",
          options: [
            { label: "Deutschland", value: "DE" },
            { label: "Österreich", value: "AT" },
            { label: "Schweiz", value: "CH" },
            { label: "Frankreich", value: "FR" },
            { label: "Italien", value: "IT" },
          ],
        },
      },
    ],
  },
};
