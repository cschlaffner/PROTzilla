import { Meta } from "@storybook/react";

import { Sidebar } from "./sidebar";

export default {
  component: Sidebar,
  title: "Sidebar",
} as Meta;

const Template = () => <Sidebar runName={""} handleStepSelection={() => {}}/>;
export const Default = Template.bind({});
