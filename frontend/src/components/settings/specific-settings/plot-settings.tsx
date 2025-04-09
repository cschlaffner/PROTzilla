import { Layout, PlotData } from "plotly.js";
import { useEffect, useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled } from "styled-components";

import {
  border,
  borderColors,
  color,
  fontSize,
  fontWeight,
  spacing,
} from "../../../theme";
import { SecondaryButton } from "../../button";
import { DropdownInputField } from "../../input-fields/dropdown-input-field";
import { NumberInputField } from "../../input-fields/number-input-field";
import { TextInputField } from "../../input-fields/text-input-field";
import Plot from "../../plot/plot";
import { SectionTitle } from "../../section-title";
import { Text } from "../../text";

const SettingsDiv = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

const PlotDiv = styled.div`
  width: fit-content;
  height: fit-content;
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
`;

export const Label = styled(Text)`
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("bold")};
  color: ${color("primary")};
  margin: 4px 0;
`;

export const PlotSettings = () => {
  const examplePlot = {
    data: [
      {
        marker: { color: "#4A536A" },
        x: ["Example 1"],
        y: [0.7],
        name: "Example 1",
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
          font: { family: "Sans Serif", size: 19 },
          width: 500,
          height: 500,
          margin: { b: 50, t: 50 },
          modebar: {
            remove: ["autoScale2d", "lasso", "lasso2d", "toImage", "select2d"],
          },
          plot_bgcolor: "white",
          title: {
            font: { family: "Sans Serif", size: 27 },
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
      legend: { tracegroupgap: 0 },
      barmode: "relative",
      title: { text: "<b>Example plot</b>" },
    },
  };

  // To do: Remove default values when API is available
  const [fileFormat, setFileFormat] = useState<string>("svg");
  const [width, setWidth] = useState<number>(50);
  const [height, setHeight] = useState<number>(30);
  const [selectedFont, setFont] = useState<string>("Arial");
  const [customFont, setCustomFont] = useState<string>("Ubuntu Mono");
  const [headingSize, setHeadingSize] = useState<number>(15);
  const [textSize, setTextSize] = useState<number>(10);
  const [plot, updatePlot] = useState(examplePlot);

  useEffect(() => {
    const sizeRatio = width / height;
    const displayedWidth = 400;
    const displayedHeight = Math.round(displayedWidth / sizeRatio);
    console.log("ratio", sizeRatio);
    console.log("width", displayedWidth);
    console.log("height", displayedHeight);
    updatePlot((prevPlot) => ({
      ...prevPlot,
      layout: {
        ...prevPlot.layout,
        width: displayedWidth,
        height: displayedHeight,
        template: {
          layout: {
            ...prevPlot.layout.template.layout,
            font: {
              ...prevPlot.layout.template.layout.font,
              family: selectedFont,
              size: textSize,
            },
            title: {
              ...prevPlot.layout.template.layout.title,
              font: {
                ...prevPlot.layout.template.layout.title.font,
                family: selectedFont,
                size: headingSize,
              },
            },
          },
        },
      },
    }));
  }, [selectedFont, headingSize, textSize, width, height]);

  const handleFileFormatChange = (value: string) => {
    setFileFormat(value);
  };
  const handleWidthChange = (value: number) => {
    setWidth(value);
  };
  const handleHeightChange = (value: number) => {
    setHeight(value);
  };
  const handleFontChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newFont =
      event.target.value === "Custom font" ? customFont : event.target.value;
    setFont(newFont);
  };

  const handleCustomFontChange = (value: string) => {
    setCustomFont(value);
  };
  const handleHeadingSizeChange = (value: number) => {
    setHeadingSize(value);
  };
  const handleTextSizeChange = (value: number) => {
    setTextSize(value);
  };
  const handleSaving = () => {
    console.log("Saving is not implemented yet.");
  };

  const fonts = [
    "Arial",
    "Courier New",
    "Helvetica",
    "Sans Serif",
    "Times New Roman",
  ];
  const isCustomSelected = !fonts.includes(selectedFont);

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Configurations for Plot Exports"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={
          "The configurations made here are automatically applied to all exported plots from PROTzilla."
        }
        style={{ paddingBottom: "20px" }}
      />
      <Row>
        <Col md={6}>
          <SettingsDiv>
            <SectionTitle baseComponent={"h5"} title={"Format and Size"} />
            <DropdownInputField
              options={[
                { value: "eps", label: "eps" },
                { value: "jpg", label: "jpg" },
                { value: "pdf", label: "pdf" },
                { value: "png", label: "png" },
                { value: "svg", label: "svg" },
                { value: "tiff", label: "tiff" },
              ]}
              onChange={handleFileFormatChange}
              label={"File format"}
              value={fileFormat}
            />
            <Row justify="between" align="center">
              <Col>
                <NumberInputField
                  label={"Width"}
                  min={10}
                  max={300}
                  step={1}
                  separateSuffix={"mm"}
                  isInteger={true}
                  onChange={handleWidthChange}
                  value={width}
                />
              </Col>
              <Col>
                <NumberInputField
                  label={"Height"}
                  min={10}
                  max={300}
                  step={1}
                  separateSuffix={"mm"}
                  isInteger={true}
                  onChange={handleHeightChange}
                  value={height}
                />
              </Col>
            </Row>
            <SectionTitle
              baseComponent={"h5"}
              title={"Text"}
              style={{ paddingTop: "4px", paddingBottom: "4px" }}
            />
            <div>
              <Label text={"Font"} />
              <div
                style={{ display: "flex", gap: "1rem", alignItems: "center" }}
              >
                {fonts.map((font) => {
                  const formattedId = `radio${font.replace(/\s/g, "")}`;
                  return (
                    <div
                      key={font}
                      style={{ display: "flex", alignItems: "center" }}
                    >
                      <input
                        type="radio"
                        id={formattedId}
                        name="fontGroup"
                        value={font}
                        checked={selectedFont === font}
                        onChange={handleFontChange}
                      />
                      <label htmlFor={formattedId}>{font}</label>
                    </div>
                  );
                })}
              </div>
              <div
                style={{ display: "flex", gap: "1rem", alignItems: "center" }}
              >
                <div>
                  <input
                    type="radio"
                    id={"radioCustomFont"}
                    name="fontGroup"
                    value="Custom font"
                    checked={isCustomSelected}
                    onChange={handleFontChange}
                  />
                  <label htmlFor={"radioCustomFont"}>{"Custom font:"}</label>
                </div>
                <div style={{ flexGrow: 1 }}>
                  <TextInputField
                    placeholder="Custom font name"
                    onChange={handleCustomFontChange}
                    value={customFont}
                  />
                </div>
              </div>
            </div>
            <Row justify="between" align="center">
              <Col>
                <NumberInputField
                  label={"Heading size"}
                  min={1}
                  max={100}
                  step={1}
                  separateSuffix={"pt"}
                  isInteger={true}
                  onChange={handleHeadingSizeChange}
                  value={headingSize}
                />
              </Col>
              <Col>
                <NumberInputField
                  label={"Text size"}
                  min={10}
                  max={300}
                  step={1}
                  separateSuffix={"pt"}
                  isInteger={true}
                  onChange={handleTextSizeChange}
                  value={textSize}
                />
              </Col>
            </Row>
          </SettingsDiv>
        </Col>
        <Col md={6}>
          <PlotDiv>
            <Plot
              styleProps={{ margin: "2px" }}
              data={plot.data as Partial<PlotData>[]}
              layout={plot.layout as Partial<Layout>}
            />
          </PlotDiv>
        </Col>
      </Row>

      <SecondaryButton text={"Save"} onPress={handleSaving} />
    </div>
  );
};
