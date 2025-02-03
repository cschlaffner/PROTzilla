import React from "react";
import { FrameInputFieldProps } from "./frame-input-field.props";
import { InputLabel } from "../../text";
import { FlexColumn } from "../../box";
import styled from "styled-components";
import { spacing } from "../../../theme";

const StyledInputFrame = styled.div`
  padding: ${spacing("small")};
  border: 2px solid #ccc;
  border-radius: ${spacing("small")};
  background-color:#FFF;

  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
`;



export const FrameInputField : React.FC<FrameInputFieldProps> = ({ label, children}) => {
  return (
    <FlexColumn>
      <InputLabel
        className="label"
        text={label}
      />
      <StyledInputFrame>
        {children}
      </StyledInputFrame>
    </FlexColumn>
  )
};