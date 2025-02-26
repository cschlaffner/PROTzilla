import { useEffect, useState } from "react";

export const useFetch = (url: string) => {
    const [fetchedData, setFetchedData] = useState([]);

    useEffect(() => {
      fetch("http://127.0.0.1:8000/api/" + url)
        .then((response) => response.json())
        .then((data) => { setFetchedData(data); });
    }, []);
    console.log(fetchedData);
    return fetchedData;
};