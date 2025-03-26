import { StoryFn } from "@storybook/react";
import {RunsTable} from "./runs-table";
import { RunsTableProps } from "./runs-table.props";

export default {
    component: RunsTable,
    parameters: {
        backgrounds: {
          default: "white",
        },
      },    
      title: "Run Table"
};

const Template: StoryFn<RunsTableProps> = (args) => <RunsTable {...args} />;

export const Default = Template.bind({});
Default.args = {
};
