import { DataTable } from "./data-table";
import { DataTableProps } from "./data-table.props";

export default {
  component: DataTable,
  title: "Data Table",
};

export const Default = (args: DataTableProps): React.ReactNode => {
  return <DataTable {...args} runName={"default"} tableLabel={"protein_df"} />;
};

Default.args = {
  pageSize: 5,
  pageSizeOptions: [5, 25, 50],
  data: [],
};
