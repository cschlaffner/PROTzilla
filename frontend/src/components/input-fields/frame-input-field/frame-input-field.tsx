import React from "react";
import { FrameInputFieldProps } from "./frame-input-field.props";
import { InputLabel } from "../../text";
import { FlexColumn, FlexRow } from "../../box";
import styled from "styled-components";
import { spacing } from "../../../theme";

const StyledInputFrame = styled.div`
  border: 2px solid #ccc;
  border-radius: ${spacing("small")};
  background-color:#FFF;

  //box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
`;

const StyledFlexRow = styled(FlexRow)`
  gap: ${spacing("small")};
  alignItems: "center"
`;

export const FrameInputField : React.FC<FrameInputFieldProps> = ({
  label, 
  labelPosition = "top",
  children
}) => {
  const Wrapper = labelPosition === "top" ? FlexColumn : StyledFlexRow;
  const formattedLabel = labelPosition === "side" && label ? `${label}:` : label;
  return (
    <Wrapper>
      <InputLabel
        className="label"
        text={formattedLabel}
      />
      <StyledInputFrame>
        {children}
      </StyledInputFrame>
    </Wrapper>
    );
};