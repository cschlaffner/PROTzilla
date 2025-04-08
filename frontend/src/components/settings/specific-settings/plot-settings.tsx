import { useState } from "react";
import { Col, Row } from "react-grid-system";
import { styled } from "styled-components";

import { color, fontSize, fontWeight, spacing } from "../../../theme";
import { DropdownInputField } from "../../input-fields/dropdown-input-field";
import { NumberInputField } from "../../input-fields/number-input-field";
import { TextInputField } from "../../input-fields/text-input-field";
import { SectionTitle } from "../../section-title";
import { Text } from "../../text";

const SettingsDiv = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

export const Label = styled(Text)`
  font-size: ${fontSize("default")};
  font-weight: ${fontWeight("bold")};
  color: ${color("primary")};
  margin: 4px 0;
`;

export const PlotSettings = () => {
    // To do: Remove default values when API is available
    const [fileFormat, setFileFormat] = useState<string>("svg");
    const [width, setWidth] = useState<number>(85);
    const [height, setHeight] = useState<number>(60);
    const [selectedFont, setFont] = useState<string>("Sans Serif");
    const [customFont, setCustomFont] = useState<string>("Comic Sans");
    const [headingSize, setHeadingSize] = useState<number>(11);
    const [textSize, setTextSize] = useState<number>(8); 

    function handleFileFormatChange(value: string): void {
        setFileFormat(value);
    }
    function handleWidthChange(value: number): void {
        setWidth(value);
    }
    function handleHeightChange(value: number): void {
        setHeight(value);
    }
    const handleFontChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setFont(event.target.value);
    };
    const handleCustomFontChange = (value: string) => {
        setCustomFont(value);
    };
    function handleHeadingSizeChange(value: number): void {
        setHeadingSize(value);
    }
    function handleTextSizeChange(value: number): void {
        setTextSize(value);
    }
    
    const fonts = [
        "Arial",
        "Courier New",
        "Helvetica",
        "Sans Serif",
        "Times New Roman"
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
            <SectionTitle
                baseComponent={"h5"}
                title={"Format and Size"}
            />
            <SettingsDiv>
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
                <Row
                    justify="between"
                    align="center"
                >
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
                    style={{ paddingTop: "4px", paddingBottom: "4px"}}
                />
                <div>
                    <Label
                        text={"Font"} 
                    />
                    <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                        {fonts.map((font) => {
                        const formattedId = `radio${font.replace(/\s/g, "")}`;
                        return (
                            <div key={font} style={{ display: "flex", alignItems: "center" }}>
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
                    <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                        <div>
                            <input
                                type="radio"
                                id={"radioCustomFont"}
                                name="fontGroup"
                                value="Eine eigene Schriftart"
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
                    </div >
                </div>
                <Row
                    justify="between"
                    align="center"
                >
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
        </div>
    )
};