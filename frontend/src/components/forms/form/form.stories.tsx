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
    input_fields: [
      {
        type: "text",
        name: "username",
        isVisible: true,
        label: "Username",
      },
      {
        type: "number",
        name: "age",
        isVisible: true,
        label: "Age",
      },
      {
        type: "multi-select",
        name: "country",
        label: "Country",
        isVisible: true,
        options: [
          { label: "Deutschland", value: "DE" },
          { label: "Österreich", value: "AT" },
          { label: "Schweiz", value: "CH" },
          { label: "Frankreich", value: "FR" },
          { label: "Italien", value: "IT" },
        ],
      },
    ],
  },
};

export const submit = Template.bind({});
submit.args = {
  formData: {
    label: "Formular Demo",
    isAutoSubmit: false,
    input_fields: [
      {
        type: "text",
        name: "username",
        isVisible: true,
        label: "Username",
      },
      {
        type: "number",
        name: "age",
        isVisible: true,
        label: "Age",
      },
      {
        type: "multi-select",
        name: "country",
        isVisible: true,
        label: "Country",
        options: [
          { label: "Deutschland", value: "DE" },
          { label: "Österreich", value: "AT" },
          { label: "Schweiz", value: "CH" },
          { label: "Frankreich", value: "FR" },
          { label: "Italien", value: "IT" },
        ],
      },
      {
        type: "file",
        name: "file",
        isVisible: true,
        label: "File",
      },
      {
        type: "dropdown",
        name: "country-drop",
        label: "Dropdown",
        isVisible: true,
        options: [
          { label: "Deutschland", value: "DE" },
          { label: "Österreich", value: "AT" },
          { label: "Schweiz", value: "CH" },
          { label: "Frankreich", value: "FR" },
          { label: "Italien", value: "IT" },
          ],
      },
    ],
  },
};
