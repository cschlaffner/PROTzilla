import { GridRowsProp } from "@mui/x-data-grid";
import React, { useEffect, useState } from "react";

import { DataTable } from "./data-table";
import { DataTableProps } from "./data-table.props";

export default {
    component: DataTable,
    title: "Data Table",
};

export const Default = (args: DataTableProps): React.ReactNode => {
    const [data, setData] = useState<GridRowsProp>([]);

    useEffect(() => {
        fetch("/data.json")
            .then((res) => res.json())
            .then((data) => { setData(data); }) 
            .catch((error: unknown) => {
                console.error("Error loading data:", error);
            });
    }, []);

    return <DataTable {...args} data={data} />;
};

Default.args = {
    pageSize: 5,
    pageSizeOptions: [5, 25, 50],
    data: [],
};