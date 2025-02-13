import { Meta, StoryFn } from "@storybook/react";
import { FrameInputField } from "./frame-input-field";
import { FrameInputFieldProps } from "./frame-input-field.props";

export default {
  component: FrameInputField,
  title: "Input Fields / Frame Input Field",
} as Meta<FrameInputFieldProps>;

const FrameTemplate: StoryFn<FrameInputFieldProps> = (args) => (
  <FrameInputField {...args}>
    <div>
      <p>Just a text field.</p>
    </div>
  </FrameInputField>
);

export const primary = FrameTemplate.bind({});
primary.args = {
  label: "Your Input Frame",
};

export const smallFrame = FrameTemplate.bind({});
smallFrame.args = {
  label: "Your Input Frame",
  smallFrame: true,
};

export const sideLabel = FrameTemplate.bind({});
sideLabel.args = {
  label: "Your Input Frame",
  labelPosition: "side",
};

export const subscript = FrameTemplate.bind({});
subscript.args = {
  label: "Your Input Frame",
  subscript: "Fancy subscript Text",
};

export const optional = FrameTemplate.bind({});
optional.args = {
  label: "Your Input Frame",
  optional: true,
};

export const withoutLabel = FrameTemplate.bind({});
withoutLabel.args = {};

export const allAffix = FrameTemplate.bind({});
allAffix.args = {
  label: "Your Input Frame",
  inlinePrefix: "€",
  inlineSuffix: "€",
  separatePrefix: "%",
  separateSuffix: "%",
};
