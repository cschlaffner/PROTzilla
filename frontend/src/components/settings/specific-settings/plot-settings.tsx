import { styled } from "styled-components";

import { spacing } from "../../../theme";
import { DropdownInputField } from "../../input-fields/dropdown-input-field";
import { SectionTitle } from "../../section-title";

const SettingsDiv = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

export const PlotSettings = () => {
    function handleFileFormatChange(value: string): void {
        console.log(value);
    }

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
                />
                
            </SettingsDiv>
        </div>
    )
};