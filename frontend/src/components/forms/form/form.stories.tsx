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
    isAutoSubmit: true,
    hasChangeIndicator: true,
    input_fields: [
      {
        type: "text",
        name: "username",
        props: {
          label: "Username",
        },
      },
      {
        type: "number",
        name: "age",
        props: {
          label: "Age",
        },
      },
      {
        type: "multi-select",
        name: "country",
        props: {
          label: "Country",
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
    isAutoSubmit: false,
    hasChangeIndicator: true,
    input_fields: [
      {
        type: "text",
        name: "username",
        props: {
          label: "Username",
        },
      },
      {
        type: "number",
        name: "age",
        props: {
          label: "Age",
        },
      },
      {
        type: "multi-select",
        name: "country",
        props: {
          label: "Country",
          options: [
            { label: "Deutschland", value: "DE" },
            { label: "Österreich", value: "AT" },
            { label: "Schweiz", value: "CH" },
            { label: "Frankreich", value: "FR" },
            { label: "Italien", value: "IT" },
          ],
        },
      },
      {
        type: "file",
        name: "file",
        props: {
          label: "File",
        },
      },
      {
        type: "dropdown",
        name: "country-drop",
        props: {
          label: "Dropdown",
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
