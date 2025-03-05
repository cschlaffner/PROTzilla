import { createTheme, ThemeProvider } from '@mui/material/styles';
import { DataGrid, GridColDef, GridRowsProp } from '@mui/x-data-grid';
import { useMemo } from 'react';

import { getTheme } from "../theme";

import type {} from '@mui/x-data-grid/themeAugmentation';

const theme = createTheme({
  mixins: {
    MuiDataGrid: {
      containerBackground: "#4A536A",
    },
  },
  components: {
    MuiDataGrid: {
        styleOverrides: {
            root: {
              "& .MuiDataGrid-sortIcon": {
                color: "#FFFFFF", // Farbe des Sortier-Pfeils
              },
              "& .MuiDataGrid-menuIconButton": {
                color: "#FFFFFF", // Menü-Icon (drei Punkte)
              },
              "& .MuiDataGrid-filterIcon": {
                color: "#FFFFFF", // Filter-Icon
              },
              "& .MuiSvgIcon-root": {
                color: "#FFFFFF", // 🎯 Standardfarbe aller Icons (Sortierung, Filter, etc.)
              },
            },
          },
    },
  },
});

const rows: GridRowsProp = [
    {
        "id": 1,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "A0A075B6S2",
        "col3": 1297700.0
    },
    {
        "id": 2,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "A0A0A0MRZ8",
        "col3": 408600.0
    },
    {
        "id": 3,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "A0A0B4J1X5",
        "col3": 911520.0
    },
    {
        "id": 4,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "A0A0B4J1Y9",
        "col3": 225580.0
    },
    {
        "id": 5,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "A0A0C4DH68",
        "col3": "NaN"
    },
    {
        "id": 6,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "A6NDG6",
        "col3": "NaN"
    },
    {
        "id": 7,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "B9A064",
        "col3": 7446900.0
    },
    {
        "id": 8,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00154-4",
        "col3": 5029400.0
    },
    {
        "id": 9,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00299",
        "col3": 37347.0
    },
    {
        "id": 10,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00330",
        "col3": "NaN"
    },
    {
        "id": 11,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00401",
        "col3": "NaN"
    },
    {
        "id": 12,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00410-3",
        "col3": 7158.6
    },
    {
        "id": 13,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00429-6",
        "col3": 9170.7
    },
    {
        "id": 14,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00468-6",
        "col3": 22477.0
    },
    {
        "id": 15,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00499",
        "col3": 319750.0
    },
    {
        "id": 16,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00533",
        "col3": 54123.0
    },
    {
        "id": 17,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00555-6",
        "col3": "NaN"
    },
    {
        "id": 18,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00560",
        "col3": "NaN"
    },
    {
        "id": 19,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00625",
        "col3": 11137.0
    },
    {
        "id": 20,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00754",
        "col3": 4767.8
    },
    {
        "id": 21,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O00764",
        "col3": 545630.0
    },
    {
        "id": 22,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14531",
        "col3": 2844200.0
    },
    {
        "id": 23,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14594",
        "col3": 4410100.0
    },
    {
        "id": 24,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14617-5",
        "col3": 21126.0
    },
    {
        "id": 25,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14737",
        "col3": "NaN"
    },
    {
        "id": 26,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14744",
        "col3": 605030.0
    },
    {
        "id": 27,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14745",
        "col3": 284640.0
    },
    {
        "id": 28,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14773-2",
        "col3": 743630.0
    },
    {
        "id": 29,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14775-3",
        "col3": 202170.0
    },
    {
        "id": 30,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14810",
        "col3": "NaN"
    },
    {
        "id": 31,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14818",
        "col3": 22137000.0
    },
    {
        "id": 32,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14841",
        "col3": "NaN"
    },
    {
        "id": 33,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O14994",
        "col3": "NaN"
    },
    {
        "id": 34,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O15020",
        "col3": 7143.2
    },
    {
        "id": 35,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O15067",
        "col3": 3395.9
    },
    {
        "id": 36,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O15075-2",
        "col3": "NaN"
    },
    {
        "id": 37,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O15144",
        "col3": 274150.0
    },
    {
        "id": 38,
        "col1": "AD01_C1_INSOLUBLE_01",
        "col2": "O15145",
        "col3": 127070.0
    }
]

const columns: GridColDef[] = [
    { field: 'col1', headerName: 'Sample', width: 200 },
    { field: 'col2', headerName: 'Protein ID', width: 160 },
    { field: 'col3', headerName: 'iBAQ', width: 120 }
]

export default function TableScreen() {
    const protzillaTheme = useMemo(() => getTheme("light"), []);
    return (   
        <ThemeProvider theme={theme}>
            <DataGrid
                rows={rows}
                columns={columns}
                sx={{
                    "& .MuiDataGrid-columnHeaders": {
                    color: "white",
                    },
                    "& .MuiDataGrid-row": {
                    backgroundColor: protzillaTheme.colors.backgroundOffset,
                    color: protzillaTheme.colors.text, // Zeilen-Textfarbe
                    },
                }}
            />
        </ThemeProvider>
    );
}