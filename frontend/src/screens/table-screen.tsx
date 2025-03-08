import { GridRowsProp } from "@mui/x-data-grid";
import { useEffect, useState } from "react";

import { DataTable } from "../components/data-table";

export default function TableScreen() {
    const [rows, setRows] = useState<GridRowsProp>([]);

    useEffect(() => {
        fetch("/data.json")
            .then((res) => res.json())
            .then((data) => { setRows(data) }) 
            .catch((error: unknown) => {
                console.error("Error loading data:", error);
            });
    }, []);

    return (
        <div>
            <DataTable data={rows}/>
        </div>
    );
}