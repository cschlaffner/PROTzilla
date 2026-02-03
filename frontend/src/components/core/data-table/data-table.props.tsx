import { GridRowsProp } from "@mui/x-data-grid";

export interface DataTableProps {
  runName: string;
  tableLabel: string;
  pageSize?: number;
  pageSizeOptions?: number[];
}
