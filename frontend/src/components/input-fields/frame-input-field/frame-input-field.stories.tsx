import { Meta, StoryFn } from "@storybook/react";
import { FrameInputField } from "./frame-input-field";
import { FrameInputFieldProps } from "./frame-input-field.props";

export default {
    component: FrameInputField,
    title: "Input Fields / Input Field Frame",
} as Meta<FrameInputFieldProps>;


const FrameTemplate: StoryFn<FrameInputFieldProps> = (args) => (
  <FrameInputField {...args}>
    <p>Just a text field.</p>
  </FrameInputField>
);

export const frame = FrameTemplate.bind({});
frame.args = {
  label: "Your Input Frame",
}


const WithoutLabelTemplate: StoryFn<FrameInputFieldProps> = (args) => (
  <FrameInputField {...args}>
    <p>Just a text field.</p>
  </FrameInputField>
);

export const withoutLabel = WithoutLabelTemplate.bind({});
withoutLabel.args = {
};


const TestInputFieldTemplate: StoryFn<FrameInputFieldProps> = (args) => (
  <FrameInputField {...args}>
    <input type="text" placeholder={args.placeholder} className="w-full bg-transparent outline-none"/>
  </FrameInputField>
);

export const testInputField = TestInputFieldTemplate.bind({});
testInputField.args = {
  label: "Your Input Field",
  placeholder: "Enter something - no function",
};