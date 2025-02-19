import { Meta, StoryFn } from "@storybook/react";
import { styled } from "styled-components";

import { Table } from "./table";
import { TableColumnProps, TableProps } from "./table.props";
import { spacing } from "../../theme";
import { FlexRow } from "../box";
import { Button, RedButton } from "../button";

interface SampleRowData {
  id: number;
  name: string;
}

const ActionRow = styled(FlexRow)`
  gap: ${spacing("small")};
  justify-content: flex-end;
  width: 100%;
`;

const columns: TableColumnProps<
  SampleRowData,
  keyof SampleRowData | "actions"
>[] = [
  { name: "id", titleTx: "ID" },
  { name: "name", titleTx: "Name" },
  {
    name: "actions",
    formatCell: () => (
      <ActionRow>
        <Button icon="add" />
        <RedButton icon="add" />
      </ActionRow>
    ),
  },
];

const rows: SampleRowData[] = [
  {
    id: 1234567,
    name: "Test",
  },
  {
    id: 1234568,
    name: "Test2",
  },
  {
    id: 1234569,
    name: "Test3",
  },
];

export default {
  title: "Table",
  component: Table,
} as Meta;

const Template: StoryFn<TableProps<SampleRowData, "actions">> = (args) => (
  <Table {...args} />
);

export const Default = Template.bind({});
Default.args = {
  columns,
  rows,
};

export const NoItems = Template.bind({});
NoItems.args = {
  columns,
  rows: [],
};
