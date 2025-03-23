import { createTheme, ThemeProvider } from "@mui/material/styles";
import {
  DataGrid,
  GridColDef,
  GridColumnVisibilityModel,
  GridPaginationModel,
  GridRowsProp,
} from "@mui/x-data-grid";
import React, { useMemo, useState } from "react";

import { DataTableProps } from "./data-table.props";
import { getTheme } from "../../theme";

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
            return 'NaN';
          }
          return value;
        },
      } as GridColDef;
    });
    

  const protzillaTheme = useMemo(() => getTheme("light"), []);

  const theme = createTheme({
    mixins: {
      MuiDataGrid: { containerBackground: protzillaTheme.colors.primary },
    },
    components: {
      MuiDataGrid: {
        styleOverrides: {
          root: {
            "& .MuiDataGrid-sortIcon": {
              color: protzillaTheme.colors.background,
            },
            "& .MuiDataGrid-menuIconButton": {
              color: protzillaTheme.colors.background,
            },
            "& .MuiDataGrid-filterIcon": {
              color: protzillaTheme.colors.background,
            },
          },
        },
      },
    },
  });

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
          fontFamily: protzillaTheme.fonts.defaultWithFallbacks,
          "& .MuiDataGrid-row": {
            backgroundColor: protzillaTheme.colors.background,
            color: protzillaTheme.colors.text,
          },
          "& .MuiSelect-select": {
            fontFamily: protzillaTheme.fonts.defaultWithFallbacks,
            color: protzillaTheme.colors.text,
          },
          "& .MuiDataGrid-columnHeaders": {
            color: protzillaTheme.colors.background,
          },
          "& .MuiDataGrid-columnHeaderTitle": { fontWeight: "bold" },
          "& .MuiTablePagination-selectLabel": {
            fontFamily: protzillaTheme.fonts.defaultWithFallbacks,
            color: protzillaTheme.colors.text,
          },
          "& .MuiTablePagination-displayedRows": {
            fontFamily: protzillaTheme.fonts.defaultWithFallbacks,
            color: protzillaTheme.colors.text,
          },
          "& .MuiDataGrid-footerContainer": {
            backgroundColor: protzillaTheme.colors.gray,
          },
        }}
      />
    </ThemeProvider>
  );
};

export default DataTable;
