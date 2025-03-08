import { GridRowsProp } from "@mui/x-data-grid";
import { useEffect, useState } from "react";

import { DataTable } from "../components/data-table";

export default function TableScreen() {
    const [data, setData] = useState<GridRowsProp>([]);

    useEffect(() => {
        fetch("/data.json")
            .then((res) => res.json())
            .then((data) => { setData(data) }) 
            .catch((error: unknown) => {
                console.error("Error loading data:", error);
            });
    }, []);

    return (
        <div>
            <DataTable data={data} pageSize={10} pageSizeOptions={[5, 10, 25]}/>
        </div>
    );
}