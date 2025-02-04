import React, { useEffect, useState } from "react";
import PlotComponent from "../components/plot/plot";

const PlotScreen = () => {
  const [plotData, setPlotData] = useState<any[]>([]);
  const [plotLayout, setPlotLayout] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/plot")
      .then((response) => response.json())
      .then((data) => {
        setPlotData(data.data);
        setPlotLayout(data.layout);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching plot data:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h3>This is a plot screen</h3>
      {loading ? <p>Loading plot...</p> : <PlotComponent data={plotData} layout={plotLayout} />}
    </div>
  );
};

export default PlotScreen;