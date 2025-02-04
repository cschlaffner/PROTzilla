import React, { useRef } from "react";
import { FrameInputFieldProps } from "./frame-input-field.props";
import { InputLabel } from "../../text";
import { FlexColumn, FlexRow } from "../../box";
import styled from "styled-components";
import { fontSize, spacing, border, borderColors } from "../../../theme";

const StyledInputFrame = styled.div`
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  background-color: white;
  display: flex;
  gap: ${spacing("verySmall")};
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
`;

const StyledFlexRow = styled(FlexRow)`
  gap: ${spacing("small")};
  align-items: "center";
`;

const StyledSeparateAffix = styled.div`
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("verySmall")};
  background: #eee;
  display: flex;
  align-items: center;
  box-sizing: content-box;
`;

const StyledSeparatePrefix = styled(StyledSeparateAffix)`
  border-right: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: calc(${border("defaultRadius")} - ${border("defaultStrength")}) 0 0
    calc(${border("defaultRadius")} - ${border("defaultStrength")});
`;

const StyledSeparateSuffix = styled(StyledSeparateAffix)`
  border-left: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: 0 calc(${border("defaultRadius")} - ${border("defaultStrength")})
    calc(${border("defaultRadius")} - ${border("defaultStrength")}) 0;
`;

const StyledInputContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing("verySmall")};
  cursor: pointer;
`;

const StyledInlineAffix = styled.span`
  display: flex;
  align-items: center;
`;

const StyledInlinePrefix = styled(StyledInlineAffix)`
  padding-left: ${spacing("small")};
`;

const StyledInlineSuffix = styled(StyledInlineAffix)`
  padding-right: ${spacing("small")};
`;

const getChildStyle = () => ({
  padding: "10px",
  border: "none",
  outline: "none",
  background: "transparent",
});

export const FrameInputField: React.FC<FrameInputFieldProps> = ({
  label,
  labelPosition = "top",
  children,
  inlinePrefix,
  inlineSuffix,
  separatePrefix,
  separateSuffix,
}) => {
  const Wrapper = labelPosition === "top" ? FlexColumn : StyledFlexRow;
  const formattedLabel =
    labelPosition === "side" && label ? `${label}:` : label;

  const inputRef = useRef<HTMLInputElement | null>(null);
  const handleClick = () => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const styledChildren = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child as React.ReactElement<any>, {
        style: getChildStyle(),
        ref: inputRef,
      });
    }
    return child;
  });

  return (
    <Wrapper>
      <InputLabel className="label" text={formattedLabel} />
      <StyledInputFrame>
        {separatePrefix && (
          <StyledSeparatePrefix>{separatePrefix}</StyledSeparatePrefix>
        )}
        <StyledInputContainer onClick={handleClick}>
          {inlinePrefix && (
            <StyledInlinePrefix>{inlinePrefix}</StyledInlinePrefix>
          )}
          {styledChildren}
          {inlineSuffix && (
            <StyledInlineSuffix>{inlineSuffix}</StyledInlineSuffix>
          )}
        </StyledInputContainer>
        {separateSuffix && (
          <StyledSeparateSuffix>{separateSuffix}</StyledSeparateSuffix>
        )}
      </StyledInputFrame>
    </Wrapper>
  );
};
