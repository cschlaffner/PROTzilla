import { useNotification } from "@protzilla/app";
import { InputContainer, SecondaryButton } from "@protzilla/core";
import { useFilePicker } from "@protzilla/hooks";
import { size, spacing } from "@protzilla/theme";
import axios from "axios";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { FileInputFieldProps } from "./file-input-field.props";


const StyledDiv = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: ${spacing("verySmall")};
  width: 100%;
  padding: 0px ${spacing("verySmall")};
  white-space: nowrap;
  height: ${size("inputFieldHeightDefault")};
`;

const StyledSpan = styled.span`
  overflow-x: auto;
  white-space: nowrap;
`;

export const FileInputField: React.FC<FileInputFieldProps> = ({
  value = null,
  placeholder = "No file chosen",
  onChange,
  ...props
}) => {
  const notify = useNotification();

  const [file, setFile] = useState<File | null>(null);
  const [currentName, setCurrentName] = useState(value);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    setCurrentName(value);
  }, [value]);

  useEffect(() => {
    if (file) {
      const fileName = file.name;
      setCurrentName(fileName);
      void handleUpload();
      onChange(fileName);
    }
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [file]);

  const handleFileSelection = (e: Event) => {
    const input = e.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const selectedFile = input.files[0];
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    setIsUploading(true);

    try {
      await axios.post("/api/upload_file/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total ?? 1));
          setUploadProgress(percent);
        },
      });

      // Upload successful
    } catch (err) {
      console.error("Upload failed:", err);
      notify({
        title: "Upload failed",
        message: "There was an error uploading the file: " + (err as string),
        type: "error",
      });
      // Upload failed
    } finally {
      setIsUploading(false);
    }
  };

  const openFilePicker = useFilePicker(handleFileSelection, "*/*", false);

  return (
    <InputContainer {...props}>
      <StyledDiv>
        <StyledSpan>{currentName ?? placeholder}</StyledSpan>
        <SecondaryButton isSmall onClick={openFilePicker}>
          Choose File
        </SecondaryButton>
      </StyledDiv>
      {isUploading && (
        <div>
          <p>Uploading: {uploadProgress}%</p>
        </div>
      )}
    </InputContainer>
  );
};
