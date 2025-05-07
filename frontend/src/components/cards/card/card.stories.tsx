import { Meta, StoryFn } from "@storybook/react";

import { Card } from "./card";
import { CardProps } from "./card.props";

export default {
  component: Card,
  title: "Card",
} as Meta<CardProps>;

const Template: StoryFn<CardProps> = (args) => <Card {...args} />;

export const Default = Template.bind({});
Default.args = {
  title: "Card Title",
  children: <p>This is a card with content inside.</p>,
};
