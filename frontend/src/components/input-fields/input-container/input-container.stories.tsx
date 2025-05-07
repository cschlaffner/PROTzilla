import { Meta, StoryFn } from "@storybook/react";
import { styled } from "styled-components";

import { InputContainer } from "./input-container";
import { InputContainerProps } from "./input-container.props";
import { size, spacing } from "../../../theme";

export default {
  component: InputContainer,
  title: "Input Fields / Frame Input Field",
} as Meta<InputContainerProps>;

const StyledDiv = styled.div<{ $isSmall: boolean }>`
  display: flex;
  align-items: center;
  padding: 0px ${spacing("small")};
  height: ${({ $isSmall }) =>
    size($isSmall ? "inputFieldHeightSmall" : "inputFieldHeightDefault")};
`;

const FrameTemplate: StoryFn<InputContainerProps> = (args) => (
  <InputContainer {...args}>
    <StyledDiv $isSmall={args.isSmall ?? false}>
      <p>Just a text field.</p>
    </StyledDiv>
  </InputContainer>
);

export const primary = FrameTemplate.bind({});
primary.args = {
  label: "Your Input Frame",
};

export const smallFrame = FrameTemplate.bind({});
smallFrame.args = {
  label: "Your Input Frame",
  isSmall: true,
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
