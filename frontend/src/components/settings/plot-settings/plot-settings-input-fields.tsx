import { styled, useTheme } from "styled-components";

import {
  DropdownInputField,
  NumberInputField,
  NumberInputFieldProps,
  TextInputField,
} from "../../../components";
import { color, spacing } from "../../../theme";

const StyledRadio = styled.input.attrs({ type: "radio" })`
  accent-color: ${color("primary")};
  margin-right: ${spacing("superSmall")};
`;

// File format: Dropdown
export interface FileFormatFieldProps {
  value: string;
  onChange: (value: string) => void;
}
export const FileFormatField: React.FC<FileFormatFieldProps> = ({
  value,
  onChange,
}) => {
  const fileFormatOptions = [
    { value: "eps", label: "eps" },
    { value: "jpeg", label: "jpeg" },
    { value: "pdf", label: "pdf" },
    { value: "png", label: "png" },
    { value: "svg", label: "svg" },
    { value: "tiff", label: "tiff" },
    { value: "webp", label: "webp" },
  ];
  return (
    <DropdownInputField
      options={fileFormatOptions}
      onChange={onChange}
      label="File format"
      value={value}
    />
  );
};

// Width: Number
export const WidthField: React.FC<NumberInputFieldProps> = ({
  value,
  onChange,
}) => {
  return (
    <NumberInputField
      label={"Width"}
      min={10}
      max={300}
      step={1}
      hasStepButtons={true}
      separateSuffix={"mm"}
      isInteger={true}
      onChange={onChange}
      value={value}
    />
  );
};

// Height: Number
export const HeightField: React.FC<NumberInputFieldProps> = ({
  value,
  onChange,
}) => {
  return (
    <NumberInputField
      label={"Height"}
      min={10}
      max={300}
      step={1}
      hasStepButtons={true}
      separateSuffix={"mm"}
      isInteger={true}
      onChange={onChange}
      value={value}
    />
  );
};

// Fonts: Radios
const fonts = [
  "Arial",
  "Courier New",
  "Helvetica",
  "Sans Serif",
  "Times New Roman",
];
export interface FontFieldProps {
  selectedFont: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}
export const FontField: React.FC<FontFieldProps> = ({
  selectedFont,
  onChange,
}) => {
  const theme = useTheme();
  return (
    <div
      style={{
        display: "flex",
        gap: theme.spacing.small,
        alignItems: "center",
      }}
    >
      {fonts.map((font) => {
        const formattedId = `radio${font.replace(/\s/g, "")}`;
        return (
          <div key={font} style={{ display: "flex", alignItems: "center" }}>
            <StyledRadio
              type="radio"
              id={formattedId}
              name="fontGroup"
              value={font}
              checked={selectedFont === font}
              onChange={onChange}
            />
            <label htmlFor={formattedId}>{font}</label>
          </div>
        );
      })}
    </div>
  );
};

// Custom font: Radio & Text
export interface CustomFontFieldProps {
  selectedFont: string;
  customFont: string;
  onChange: (value: string) => void;
}
export const CustomFontField: React.FC<CustomFontFieldProps> = ({
  selectedFont,
  customFont,
  onChange,
}) => {
  const theme = useTheme();
  const isCustomSelected = !fonts.includes(selectedFont);
  return (
    <div
      style={{
        display: "flex",
        gap: theme.spacing.small,
        alignItems: "center",
      }}
    >
      <div>
        <StyledRadio
          type="radio"
          id={"radioCustomFont"}
          name="fontGroup"
          value={customFont}
          checked={isCustomSelected}
          onChange={(e) => {
            onChange(e.target.value);
          }}
        />
        <label htmlFor={"radioCustomFont"}>{"Custom font:"}</label>
      </div>
      <div style={{ flexGrow: 1 }}>
        <TextInputField
          placeholder="Custom font name"
          onChange={onChange}
          value={customFont}
        />
      </div>
    </div>
  );
};

// Title size: Number
export const TitleSizeField: React.FC<NumberInputFieldProps> = ({
  value,
  onChange,
}) => {
  return (
    <NumberInputField
      label={"Title size"}
      min={1}
      max={100}
      step={1}
      hasStepButtons={true}
      separateSuffix={"pt"}
      isInteger={true}
      value={value}
      onChange={onChange}
    />
  );
};

// Text size: Number
export const TextSizeField: React.FC<NumberInputFieldProps> = ({
  value,
  onChange,
}) => {
  return (
    <NumberInputField
      label={"Text size"}
      min={1}
      max={100}
      step={1}
      hasStepButtons={true}
      separateSuffix={"pt"}
      isInteger={true}
      onChange={onChange}
      value={value}
    />
  );
};
