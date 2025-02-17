import { Meta } from "@storybook/react";
import React from "react"

import { Sidebar } from "./sidebar"
// import type { SidebarProps } from "./sidebar.props";

export default {
    component: Sidebar,
    title: "Sidebar"
} as Meta;

const Template = () => <Sidebar />;
export const Default = Template.bind({});
