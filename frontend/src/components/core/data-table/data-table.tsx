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
import { callApiWithParameters, TableRecord } from "@protzilla/utils";
import React, { useEffect, useMemo, useState } from "react";

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

export const DataTable: React.FC<DataTableProps> = ({
  runName,
  tableLabel,
  pageSize,
  pageSizeOptions = [10],
}) => {
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: pageSize ?? 10,
  });
  const [columnVisibilityModel, setColumnVisibilityModel] = useState<GridColumnVisibilityModel>({
    id: false,
  });
  const [currentRows, setCurrentRows] = useState<TableRecord[]>([]);
  const [totalRowCount, setTotalRowCount] = useState(0);
  const [isLoading, setLoading] = useState(false);

  // Fetch data when pagination changes
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);

      const startIndex = paginationModel.page * paginationModel.pageSize;
      const endIndex = startIndex + paginationModel.pageSize;

      try {
        const response = await callApiWithParameters("get_current_step_table_data/", {
          run_name: runName,
          table_label: tableLabel,
          start_index: startIndex,
          end_index: endIndex,
        });

        setCurrentRows(response.rows);
        setTotalRowCount(response.total_row_count);
      } catch (error) {
        console.error("Failed to fetch table data:", error);
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [paginationModel, tableLabel, runName]);

  const columns = useMemo(() => {
    if (currentRows.length === 0) return [];

    return Object.keys(currentRows[0]).map((key) => {
      const isNumeric = currentRows.every(
        (row) => typeof row[key] === "number" || row[key] === null,
      );
      return {
        field: key,
        headerName: key,
        flex: 1,
        type: isNumeric ? "number" : "string",
        align: "left",
        headerAlign: "left",
        // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
        valueFormatter: (value) => value ?? "NaN",
      } as GridColDef;
    });
  }, [currentRows]);

  const theme = useMemo(() => getMuiTheme(), []);
  const height = parseInt(baseTheme.sizes.tableRow, 10);

  return (
    <ThemeProvider theme={theme}>
      <DataGrid
        rows={currentRows}
        columns={columns}
        rowCount={totalRowCount}
        loading={isLoading}
        columnVisibilityModel={columnVisibilityModel}
        onColumnVisibilityModelChange={setColumnVisibilityModel}
        paginationMode="server"
        paginationModel={paginationModel}
        onPaginationModelChange={setPaginationModel}
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
        disableColumnSorting
        disableColumnFilter
      />
    </ThemeProvider>
  );
};

export default DataTable;
