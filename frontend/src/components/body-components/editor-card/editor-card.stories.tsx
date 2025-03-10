import { Meta, StoryFn } from "@storybook/react";

import { EditorCard } from "./editor-card";
import { EditorCardProps } from "./editor-card.props";

export default {
  component: EditorCard,
  title: "Content Card",
} as Meta<EditorCardProps>;

const Template: StoryFn<EditorCardProps> = (args) => <EditorCard {...args} />;


export const Default = Template.bind({});
Default.args = {
  listEditorComponent: <p>Hey</p>,
};
