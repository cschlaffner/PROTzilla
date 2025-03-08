import { GridRowsProp } from "@mui/x-data-grid";

export interface DataTableProps {
  data: GridRowsProp;
  pageSize?: number;
  pageSizeOptions?: number[];
}