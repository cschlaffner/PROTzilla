import { Meta, StoryFn } from "@storybook/react";

import { SearchInputField } from "./search-input-field";
import { SearchInputFieldProps } from "./search-input-field.props";

export default {
  component: SearchInputField,
  title: "Form Fields / Search",
  argTypes: { onChange: { action: "changed" } },
} as Meta<SearchInputFieldProps>;

const Template: StoryFn<SearchInputFieldProps> = (args) => {
  return <SearchInputField {...args} />;
};

export const primary = Template.bind({});
primary.args = {
  placeholder: "Search ...",
};

export const label = Template.bind({});
label.args = {
  label: "Search for something",
  placeholder: "Search ...",
  subscript: "Live Update",
};
