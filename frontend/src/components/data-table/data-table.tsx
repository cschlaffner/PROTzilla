import { ThemeProvider } from "@mui/material/styles";
import {
  DataGrid,
  GridColDef,
  GridColumnVisibilityModel,
  GridPaginationModel,
  GridRowsProp,
} from "@mui/x-data-grid";
import React, { useMemo, useState } from "react";

import { DataTableProps } from "./data-table.props";
import { getMuiTheme } from "../../theme";

export const DataTable: React.FC<DataTableProps> = ({
  data,
  pageSize,
  pageSizeOptions,
}) => {
  const [rows] = useState<GridRowsProp>(data);
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: pageSize ?? 10,
  });
  const [columnVisibilityModel, setColumnVisibilityModel] =
    useState<GridColumnVisibilityModel>({
      id: false,
    });

  const columns = Object.keys(data[0]).map((key) => {
    const isNumeric = data.every(
      (row) => typeof row[key] === "number" || row[key] === null,
    );
    return {
      field: key,
      headerName: key,
      minWidth: 200,
      flex: 1,
      type: isNumeric ? "number" : "string",
      align: "left",
      headerAlign: "left",
      valueFormatter: (value: number | null) => {
        if (value == null) {
          return "NaN";
        }
        return value;
      },
    } as GridColDef;
  });

  const theme = useMemo(() => getMuiTheme(), []);

  return (
    <ThemeProvider theme={theme}>
      <DataGrid
        rows={rows}
        columns={columns}
        columnVisibilityModel={columnVisibilityModel}
        onColumnVisibilityModelChange={(newModel) => {
          setColumnVisibilityModel(newModel);
        }}
        paginationModel={paginationModel}
        onPaginationModelChange={(newModel) => {
          setPaginationModel((prev) => ({ ...prev, ...newModel }));
        }}
        pageSizeOptions={pageSizeOptions}
        sx={{
          width: "100%",
          height: "100%",
        }}
      />
    </ThemeProvider>
  );
};

export default DataTable;
