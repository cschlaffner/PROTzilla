import { createTheme, ThemeProvider } from '@mui/material/styles';
import { DataGrid, GridColDef, GridColumnVisibilityModel, GridRowsProp } from '@mui/x-data-grid';
import { useEffect, useMemo, useState } from 'react';

import { getTheme } from "../theme";

import type {} from '@mui/x-data-grid/themeAugmentation';

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
              "& .MuiSvgIcon-root": { color: "#FFFFFF" },
            },
          },
    },
  },
});

export default function TableScreen() {
    const [rows, setRows] = useState<GridRowsProp>([]);
    const [columns, setColumns] = useState<GridColDef[]>([]);
    const [columnVisibilityModel, setColumnVisibilityModel] = useState<GridColumnVisibilityModel>({
        id: false,
    });

    useEffect(() => {
        fetch("/data.json")
            .then((res) => res.json())
            .then((data) => {
                setRows(data);
                if (data.length > 0) {
                const dynamicColumns = Object.keys(data[0]).map((key) => ({
                    field: key,
                    headerName: key,
                    flex: 1,
                }));
                setColumns(dynamicColumns);
                }
            })
            .catch((error: unknown) => {
                console.error("Error loading data:", error);
            });
    }, []);

    const protzillaTheme = useMemo(() => getTheme("light"), []);

    return (   
        <ThemeProvider theme={theme}>
            <DataGrid
                rows={rows}
                columns={columns}
                columnVisibilityModel={columnVisibilityModel}
                onColumnVisibilityModelChange={(newModel) => { setColumnVisibilityModel(newModel); }}
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
}