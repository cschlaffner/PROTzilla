import { createTheme, ThemeProvider } from "@mui/material/styles";
import { DataGrid, GridColDef, GridColumnVisibilityModel, GridPaginationModel, GridRowsProp } from "@mui/x-data-grid";
import React, { useEffect, useMemo, useState } from "react";

import { DataTableProps } from "./data-table.props";
import { getTheme } from "../../theme";

const theme = createTheme({
    mixins: {
        MuiDataGrid: { containerBackground: "#4A536A" },
    },
    components: {
        MuiDataGrid: {
            styleOverrides: {
                root: {
                "& .MuiDataGrid-sortIcon": { color: "#FFFFFF" },
                "& .MuiDataGrid-menuIconButton": { color: "#FFFFFF" },
                "& .MuiDataGrid-filterIcon": { color: "#FFFFFF" },
                },
            },
      },
    },
  });

export const DataTable: React.FC<DataTableProps> = ({ data, pageSize, pageSizeOptions }) => {
    const [rows, setRows] = useState<GridRowsProp>(data);
    const [columns, setColumns] = useState<GridColDef[]>([]);
    const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
        page: 0,
        pageSize: pageSize ?? 10,
    });
    const [columnVisibilityModel, setColumnVisibilityModel] = useState<GridColumnVisibilityModel>({
        id: false,
    });

    useEffect(() => {
        if (data.length > 0) {
            const dynamicColumns = Object.keys(data[0]).map((key) => {
                const isNumeric = data.every((row) => 
                    typeof row[key] === "number" || row[key] === null
                );
                return {
                    field: key,
                    headerName: key,
                    minWidth: 200,
                    flex: 1,
                    type: isNumeric ? "number" : "string",
                    align: "left",
                    headerAlign: "left",
                    valueFormatter: (value: number | null ) => {
                        if (value == null ) {
                            return "NaN";
                        }
                        return value;
                    },
                };
            });
            setColumns(dynamicColumns);
        }
        setRows(data);
    }, [data]);

    const protzillaTheme = useMemo(() => getTheme("light"), []);

    return (
        <ThemeProvider theme={theme}>
        <DataGrid
            rows={rows}
            columns={columns}
            columnVisibilityModel={columnVisibilityModel}
            onColumnVisibilityModelChange={(newModel) => { setColumnVisibilityModel(newModel); }}
            paginationModel={paginationModel} 
            onPaginationModelChange={(newModel) => 
                { setPaginationModel((prev) => ({ ...prev, ...newModel })); }
            }
            pageSizeOptions={pageSizeOptions}
            sx={{
                "& .MuiDataGrid-columnHeaders": { color: "white" },
                "& .MuiDataGrid-columnHeaderTitle": { fontWeight: "bold" },
                "& .MuiDataGrid-row": {
                    backgroundColor: protzillaTheme.colors.backgroundOffset,
                    color: protzillaTheme.colors.text,
                },
            }}
        />
        </ThemeProvider>
    );
};

export default DataTable;