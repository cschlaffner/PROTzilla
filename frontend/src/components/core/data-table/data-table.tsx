import { Box } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import {
  DataGrid,
  GridColDef,
  GridColumnVisibilityModel,
  GridFooterContainer,
  GridFooterContainerProps,
  GridPagination,
  GridPaginationModel,
} from "@mui/x-data-grid";
import { baseTheme, getMuiTheme } from "@protzilla/theme";
import React, { useMemo, useState } from "react";

import { DataTableProps } from "./data-table.props";

export const CustomFooter: React.FC<GridFooterContainerProps> = () => {
  return (
    <GridFooterContainer>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <GridPagination />
      </Box>
    </GridFooterContainer>
  );
};

export const DataTable: React.FC<DataTableProps> = ({ data, pageSize, pageSizeOptions }) => {
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: pageSize ?? 10,
  });
  const [columnVisibilityModel, setColumnVisibilityModel] = useState<GridColumnVisibilityModel>({
    id: false,
  });

  const columns = Object.keys(data[0]).map((key) => {
    const isNumeric = data.every((row) => typeof row[key] === "number" || row[key] === null);
    return {
      field: key,
      headerName: key,
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
  const height = parseInt(baseTheme.sizes.tableRow, 10);

  return (
    <ThemeProvider theme={theme}>
      <DataGrid
        rows={data}
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
        rowHeight={height}
        columnHeaderHeight={height}
        slots={{
          footer: CustomFooter,
        }}
      />
    </ThemeProvider>
  );
};

export default DataTable;
