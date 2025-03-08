import React from "react";

import { DataTable } from "./data-table";
import { DataTableProps } from "./data-table.props";

export default {
    component: DataTable,
    title: "DataTable",
};

export const Default = (args: DataTableProps): React.ReactNode => (
    <DataTable {...args} />
);

Default.args = {
    pageSize: 5,
    pageSizeOptions: [5, 25, 50],
    data: [
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "A0A075B6S2",
            "Gene": "NaN",
            "iBAQ": 1297700.0,
            "id": 0
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "A0A0A0MRZ8",
            "Gene": "NaN",
            "iBAQ": 408600.0,
            "id": 1
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "A0A0B4J1X5",
            "Gene": "NaN",
            "iBAQ": 911520.0,
            "id": 2
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "A0A0B4J1Y9",
            "Gene": "NaN",
            "iBAQ": 225580.0,
            "id": 3
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "A0A0C4DH68",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 4
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "A6NDG6",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 5
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "B9A064",
            "Gene": "NaN",
            "iBAQ": 7446900.0,
            "id": 6
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00154-4",
            "Gene": "NaN",
            "iBAQ": 5029400.0,
            "id": 7
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00299",
            "Gene": "NaN",
            "iBAQ": 37347.0,
            "id": 8
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00330",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 9
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00401",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 10
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00410-3",
            "Gene": "NaN",
            "iBAQ": 7158.6,
            "id": 11
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00429-6",
            "Gene": "NaN",
            "iBAQ": 9170.7,
            "id": 12
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00468-6",
            "Gene": "NaN",
            "iBAQ": 22477.0,
            "id": 13
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00499",
            "Gene": "NaN",
            "iBAQ": 319750.0,
            "id": 14
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00533",
            "Gene": "NaN",
            "iBAQ": 54123.0,
            "id": 15
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00555-6",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 16
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00560",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 17
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00625",
            "Gene": "NaN",
            "iBAQ": 11137.0,
            "id": 18
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00754",
            "Gene": "NaN",
            "iBAQ": 4767.8,
            "id": 19
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O00764",
            "Gene": "NaN",
            "iBAQ": 545630.0,
            "id": 20
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14531",
            "Gene": "NaN",
            "iBAQ": 2844200.0,
            "id": 21
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14594",
            "Gene": "NaN",
            "iBAQ": 4410100.0,
            "id": 22
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14617-5",
            "Gene": "NaN",
            "iBAQ": 21126.0,
            "id": 23
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14737",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 24
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14744",
            "Gene": "NaN",
            "iBAQ": 605030.0,
            "id": 25
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14745",
            "Gene": "NaN",
            "iBAQ": 284640.0,
            "id": 26
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14773-2",
            "Gene": "NaN",
            "iBAQ": 743630.0,
            "id": 27
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14775-3",
            "Gene": "NaN",
            "iBAQ": 202170.0,
            "id": 28
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14810",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 29
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14818",
            "Gene": "NaN",
            "iBAQ": 22137000.0,
            "id": 30
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14841",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 31
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O14994",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 32
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15020",
            "Gene": "NaN",
            "iBAQ": 7143.2,
            "id": 33
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15067",
            "Gene": "NaN",
            "iBAQ": 3395.9,
            "id": 34
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15075-2",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 35
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15144",
            "Gene": "NaN",
            "iBAQ": 274150.0,
            "id": 36
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15145",
            "Gene": "NaN",
            "iBAQ": 127070.0,
            "id": 37
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15230",
            "Gene": "NaN",
            "iBAQ": 7694.3,
            "id": 38
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15254",
            "Gene": "NaN",
            "iBAQ": 13120.0,
            "id": 39
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15394",
            "Gene": "NaN",
            "iBAQ": 81249.0,
            "id": 40
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15488-4",
            "Gene": "NaN",
            "iBAQ": 575070.0,
            "id": 41
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15511",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 42
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O15540",
            "Gene": "NaN",
            "iBAQ": 491470.0,
            "id": 43
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O43175",
            "Gene": "NaN",
            "iBAQ": 139170.0,
            "id": 44
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O43237-2",
            "Gene": "NaN",
            "iBAQ": "NaN",
            "id": 45
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O43301",
            "Gene": "NaN",
            "iBAQ": 54931.0,
            "id": 46
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O43390",
            "Gene": "NaN",
            "iBAQ": 14964.0,
            "id": 47
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O43396",
            "Gene": "NaN",
            "iBAQ": 179510.0,
            "id": 48
        },
        {
            "Sample": "AD01_C1_INSOLUBLE_01",
            "Protein ID": "O43426-4",
            "Gene": "NaN",
            "iBAQ": 129500.0,
            "id": 49
        },
    ]
};