import { Layout, PlotData } from "plotly.js";
import Plotly from "plotly.js-dist-min";
import { useState } from "react";
import Plot from "react-plotly.js";
import { styled } from "styled-components";

import { PlotDownloadSettingsProps } from "./plot-download-settings.props";
import {
  Button,
  Modal,
  SectionTitle,
} from "../../../components";
import { border, borderColors } from "../../../theme";

const StyledModal = styled(Modal)`
  width: fit-content;
  max-width: 100%;
  height: fit-content;
  max-height: 100vh;
`;

const PlotDiv = styled.div`
  width: fit-content;
  height: fit-content;
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  padding: 2px;
`;

export const PlotDownloadSettings: React.FC<PlotDownloadSettingsProps> = ({
  isOpen,
  onClose,
}) => {
  const examplePlot = {
    data: [
      {
        marker: { color: "#4A536A" },
        x: ["Example 1"],
        y: [0.7],
        name: "This is a long text for testing the width",
        type: "bar",
      },
      {
        marker: { color: "#CE5A5A" },
        x: ["Example 2"],
        y: [0.3],
        name: "Example 2",
        type: "bar",
      },
    ],
    layout: {
      template: {
        layout: {
          colorway: ["#4A536A", "#CE5A5A"],
          dragmode: "pan",
          font: { family: "Sans Serif", size: 10 },
          width: 400,
          height: 250,
          margin: { b: 55, t: 50, r: 50, l: 50 },
          modebar: {
            remove: ["autoScale2d", "lasso", "lasso2d", "toImage", "select2d"],
          },
          plot_bgcolor: "white",
          title: {
            font: { family: "Sans Serif", size: 15 },
            x: 0.5,
            xanchor: "center",
            y: 0.95,
            yanchor: "top",
          },
          yaxis: { gridcolor: "lightgrey", zerolinecolor: "lightgrey" },
        },
      },
      xaxis: { anchor: "y", domain: [0.0, 1.0], title: { text: "Example" } },
      yaxis: { anchor: "x", domain: [0.0, 1.0], title: { text: "Example" } },
      barmode: "relative",
      title: { text: "<b>Example plot</b>" },
    },
  };
  const [plot] = useState(examplePlot);

  const handleDownload = () => {
    Plotly.downloadImage("test", {
      format: "png",
      filename: "testfile",
      width: 400,
      height: 250,
      scale: 10,
    } as Plotly.DownloadImgopts).catch((error: unknown) => {
      console.error("Export failed: ", error);
    });
  };

  return (
    <StyledModal isOpen={isOpen} onClose={onClose} title="Download Plots">
      <SectionTitle
        baseComponent={"h6"}
        description={
          "All configurations entered here apply to this plot only. If you want to apply them to future plots, save them as your template."
        }
        style={{ paddingBottom: "20px" }}
      />
      <PlotDiv>
        <Plot
          data={plot.data as Partial<PlotData>[]}
          layout={plot.layout as Partial<Layout>}
          divId={"test"}
        />
      </PlotDiv>
      <Button text="Download" onPress={handleDownload} style={{marginTop: "5px"}} />
    </StyledModal>
  );
};
