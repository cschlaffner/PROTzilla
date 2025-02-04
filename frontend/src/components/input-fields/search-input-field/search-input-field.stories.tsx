import { Meta, StoryFn } from "@storybook/react";
import { SearchInputField } from "./search-input-field";
import { useState } from "react";
import { SearchInputFieldProps } from "./search-input-field.props";


export default {
    component: SearchInputField,
    title: "Input Fields / Search",
} as Meta<SearchInputFieldProps>;


const Template: StoryFn<SearchInputFieldProps> = (args) => {
  const [value, setValue] = useState<string>("");

  return <SearchInputField {...args} defaultValue={value} onChange={setValue} />;
};


export const primary = Template.bind({});
primary.args = {
  placeholder: "Search ...",
};

export const label = Template.bind({});
label.args = {
  label: "Search for something",
  placeholder: "Search ...",
};