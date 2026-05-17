import { Box } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import {
  DataGrid,
  GridColDef,
  GridColumnVisibilityModel,
  GridFilterModel,
  GridFooterContainer,
  GridFooterContainerProps,
  GridPagination,
  GridPaginationModel,
  GridSortModel,
} from "@mui/x-data-grid";
import { baseTheme, getMuiTheme, spacing } from "@protzilla/theme";
import { callApiWithParameters, TableRecord } from "@protzilla/utils";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { DataTableProps } from "./data-table.props";
import { CSVButton } from "../shared";

const StyledCSVButton = styled(CSVButton)`
  width: auto;
  align-self: flex-end;
  margin-top: ${spacing("buttonGap")};
`;

export const CustomFooter: React.FC<GridFooterContainerProps> = () => {
  return (
    <GridFooterContainer>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <GridPagination />
      </Box>
    </GridFooterContainer>
  );
};

const FALLBACK_TOO_MANY_COLUMNS = [
  {
    ERROR: "This table contains too many columns to be properly displayed within PROTzilla.",
    id: "error_too_many_columns1",
  },
  {
    ERROR: "Please download the table using the button below and view using external software.",
    id: "error_too_many_columns2",
  },
];
const MAX_COLUMNS = 25;

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
  const [sortModel, setSortModel] = useState<GridSortModel>([]);
  const [filterModel, setFilterModel] = useState<GridFilterModel>({
    items: [],
  });
  const [columns, setColumns] = useState<GridColDef[]>([]);
  const columnsInitializedRef = useRef(false);

  // necessary for updating which columns exist when switching between tables
  useEffect(() => {
    setColumns([]);
    setFilterModel({ items: [] });
    setSortModel([]);
    columnsInitializedRef.current = false;
  }, [tableLabel]);

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
          sort_field: sortModel[0]?.field,
          sort_direction: sortModel[0]?.sort ?? "asc",
          filters: JSON.stringify(filterModel.items),
        });

        if (response.rows.length > 0 && !columnsInitializedRef.current) {
          const generatedColumns = Object.keys(response.rows[0]).map((key) => {
            const isNumeric = response.rows.every(
              (row: TableRecord) => typeof row[key] === "number" || row[key] === null,
            );

            return {
              field: key,
              headerName: key,
              flex: 1,
              type: isNumeric ? "number" : "string",
              align: "left",
              headerAlign: "left",
              filterable: true,
              valueFormatter: (value: unknown) => value ?? "NaN",
            } as GridColDef;
          });

          setColumns(generatedColumns);
          columnsInitializedRef.current = true;
        }

        if (response.rows.length > 0 && Object.keys(response.rows[0]).length > MAX_COLUMNS) {
          setCurrentRows(FALLBACK_TOO_MANY_COLUMNS);
          setTotalRowCount(FALLBACK_TOO_MANY_COLUMNS.length);
        } else {
          setCurrentRows(response.rows);
          setTotalRowCount(response.total_row_count);
        }
      } catch (error) {
        console.error("Failed to fetch table data:", error);
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [paginationModel, sortModel, filterModel, tableLabel, runName]);

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
        sortingMode="server"
        sortModel={sortModel}
        onSortModelChange={setSortModel}
        filterMode="server"
        filterModel={filterModel}
        onFilterModelChange={setFilterModel}
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
      <StyledCSVButton
        runName={runName}
        tableLabel={tableLabel}
        fileName={tableLabel}
        sortModel={sortModel}
        filterModel={filterModel}
      />
    </ThemeProvider>
  );
};

export default DataTable;
