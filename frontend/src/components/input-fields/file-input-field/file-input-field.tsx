import { forwardRef, useImperativeHandle, useState } from "react";
import { styled } from "styled-components";

import { spacing} from "../../../theme";
import { FrameInputField } from "../frame-input-field";
import { FileInputFieldProps, FileInputFieldRef } from "./file-input-field.props";
import { useFilePicker } from "../../../hooks";
import { Button } from "../../button";


const StyledDiv = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: ${spacing("verySmall")};
  width: 100%;
  padding: ${spacing("verySmall")};
`;

const StyledSpan = styled.span`
  overflow-x: auto; /* Shows scrollbar only when necessary */
  white-space: nowrap; /* Prevents text from wrapping */
`;

export const FileInputField = forwardRef<FileInputFieldRef, FileInputFieldProps>(
  function FileInputField({defaultValue = null, placeholder = "No file choosen", onChange, ...props}, ref) {
    const [file, setFile] = useState<File | null>(defaultValue);
  
    const handleFileSelection = (e: Event) => {
      const input = e.target as HTMLInputElement;
      if (input.files?.length) {
        const selectedFile = input.files[0];
        setFile(selectedFile);
        onChange(selectedFile);
      }
    };

    const openFilePicker = useFilePicker(
      handleFileSelection,
      "*/*",
      false,
    );

    useImperativeHandle(ref, () => ({
      getValue: () => file,
      setValue: (newValue: File) => {
        setFile(newValue);
      },
    }));

    return (
      <FrameInputField {...props}>
        <StyledDiv>
          <StyledSpan>{file ? file.name : placeholder}</StyledSpan>
          <Button isSmall onClick={openFilePicker}>Choose File</Button>
        </StyledDiv>
      </FrameInputField>
    );
  }
);