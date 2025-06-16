import { Meta } from "@storybook/react";

import { Sidebar } from "./sidebar";

export default {
  component: Sidebar,
  title: "Sidebar",
} as Meta;

const Template = () => (
  <></>
  // <Sidebar
  //   runData={[]}
  //   runName={""}
  //   navigateOrRefreshSteps={() => {
  //     //donothing
  //   }}
  // />
);

export const Default = Template.bind({});
