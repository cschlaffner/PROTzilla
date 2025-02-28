import { forwardRef, useState } from "react";
import { styled } from "styled-components";

import { color, radius, spacing, duration } from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import { FileInputFieldProps, FileInputFieldRef } from "./file-input-field.props";
import { API_ROOT } from "../../../constants";


const StyledInput = styled.input`
  display: none;
`;

const StyledLabel = styled.label`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  height: 100%;

  background: ${color("primary")} !important;
  color: ${color("onPrimary")};
  border: solid ${color("background")} 3px !important;
  border-radius: ${radius("default")};
  padding: ${spacing("smallButtonPadding")} !important;
  box-sizing: border-box;
  cursor: pointer;
  width: auto !important;

  transition: background ${duration("shorter")}ms ease-in-out;

  &:hover {
    background: ${color("primaryHover")} !important;
  }
`;

const StyledSpan = styled.span`
  display: block; /* Ensures proper scrolling behavior */
  overflow-x: auto; /* Shows scrollbar only when necessary */
  white-space: nowrap; /* Prevents text from wrapping */
  max-width: 100%; /* Ensures it doesn't overflow parent container */
  -webkit-overflow-scrolling: touch; /* Improves mobile scrolling */
`;

export const FileInputField = forwardRef<FileInputFieldRef, FileInputFieldProps>(
  function FileInputField({ ...props }) {
    const [file, setFile] = useState<File | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files?.length) {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
      }
    };

    return (
        <FrameInputField {...props}>
          <StyledSpan>{file ? file.name : "No file choosen"}</StyledSpan>
          <StyledInput id="file-upload" type="file" onChange={handleFileChange}/>
          <StyledLabel htmlFor="file-upload">Choose File</StyledLabel>
        </FrameInputField>
    );
  }
);