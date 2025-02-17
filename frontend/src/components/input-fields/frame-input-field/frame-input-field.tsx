import React, { useRef } from "react";
import { styled } from "styled-components";

import { FrameInputFieldProps } from "./frame-input-field.props";
import {
  border,
  borderColors,
  color,
  fontSize,
  spacing,
} from "../../../theme";
import { InputLabel, Text } from "../../text";

const GridContainer = styled.div`
  align-items: center;
  display: grid;
  gap: 0px ${spacing("verySmall")};
  grid-template-columns: auto 1fr;
  padding: ${spacing("verySmall")} 0px;
`;

const GridItem = styled.div<{ row: number; col: number }>`
  grid-column: ${({ col }) => col};
  grid-row: ${({ row }) => row};
`;

const FlexContainer = styled.div`
  align-items: flex-start;
  display: flex;
  gap: ${spacing("verySmall")};
  justify-content: space-between;
  width: 100%;
`;

const StyledInputFrame = styled.div<{ $smallBorder: boolean }>`
  background-color: white;
  border: ${({ $smallBorder }) =>
      border($smallBorder ? "smallStrength" : "defaultStrength")}
    solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  display: flex;
  gap: ${spacing("verySmall")};
  // box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
  width: 100%;
`;

const StyledSeparateAffix = styled.div`
  align-items: center;
  background: ${color("gray6")};
  box-sizing: content-box;
  display: flex;
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("verySmall")};
`;

const StyledSeparatePrefix = styled(StyledSeparateAffix)`
  border-right: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: calc(${border("defaultRadius")} - ${border("defaultStrength")})
    0 0 calc(${border("defaultRadius")} - ${border("defaultStrength")});
`;

const StyledSeparateSuffix = styled(StyledSeparateAffix)`
  border-left: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: 0
    calc(${border("defaultRadius")} - ${border("defaultStrength")})
    calc(${border("defaultRadius")} - ${border("defaultStrength")}) 0;
`;

const StyledInputContainer = styled.div`
  align-items: center;
  cursor: pointer;
  display: flex;
  gap: ${spacing("verySmall")};
  width: 100%;
`;

const StyledInlineAffix = styled.span`
  align-items: center;
  display: flex;
`;

const StyledInlinePrefix = styled(StyledInlineAffix)`
  padding-left: ${spacing("small")};
`;

const StyledInlineSuffix = styled(StyledInlineAffix)`
  padding-right: ${spacing("small")};
`;

const StyledSubtitle = styled(Text)`
  color: ${color("gray50")};
  font-size: ${fontSize("small")};
  margin: ${spacing("verySmall")} 0 0 0;
  padding: 0 ${spacing("verySmall")};
`;

const StyledSubscriptText = styled(StyledSubtitle)`
  flex: 1;
  white-space: normal;
  word-break: break-word;
`;

const FixedText = styled(StyledSubtitle)`
  flex-shrink: 0;
  font-style: italic;
  margin-left: 8px;
`;

const getChildStyle = (smallFrame: boolean) => ({
  background: "transparent",
  border: "none",
  outline: "none",
  padding: smallFrame ? "5px" : "10px",
  width: "100%",
});

export const FrameInputField: React.FC<FrameInputFieldProps> = ({
  children,
  label,
  labelPosition = "top",
  optional = false,
  subscript,
  inlinePrefix,
  inlineSuffix,
  separatePrefix,
  separateSuffix,
  smallBorder = false,
  smallFrame = false,
  ...props
}) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const handleClick = () => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const styledChildren = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child as React.ReactElement, {
        style: getChildStyle(smallFrame),
        ref: inputRef,
      });
    }
    return child;
  });

  return (
    <GridContainer {...props}>
      {labelPosition === "top" ? (
        <GridItem row={1} col={2}>
          {label && (
            <InputLabel
              className="label"
              text={label}
              style={{ padding: `0 ${String(spacing("verySmall"))}` }}
            />
          )}
        </GridItem>
      ) : (
        <GridItem row={2} col={1}>
          {label && (
            <InputLabel
              className="label"
              text={label + ":"}
              style={{ padding: `0 ${String(spacing("small"))}` }}
            />
          )}
        </GridItem>
      )}
      <GridItem row={2} col={2}>
        <StyledInputFrame $smallBorder={smallBorder}>
          {separatePrefix && (
            <StyledSeparatePrefix className="separate-prefix">
              {separatePrefix}
            </StyledSeparatePrefix>
          )}
          <StyledInputContainer onClick={handleClick}>
            {inlinePrefix && (
              <StyledInlinePrefix className="inline-prefix">
                {inlinePrefix}
              </StyledInlinePrefix>
            )}
            {styledChildren}
            {inlineSuffix && (
              <StyledInlineSuffix className="inline-suffix">
                {inlineSuffix}
              </StyledInlineSuffix>
            )}
          </StyledInputContainer>
          {separateSuffix && (
            <StyledSeparateSuffix className="separate-suffix">
              {separateSuffix}
            </StyledSeparateSuffix>
          )}
        </StyledInputFrame>
      </GridItem>
      <GridItem row={3} col={2}>
        <FlexContainer>
          <StyledSubscriptText
            className="subscript"
            text={subscript}
            style={{ whiteSpace: "normal" }}
          />

          {optional && <FixedText text="optional" />}
        </FlexContainer>
      </GridItem>
    </GridContainer>
  );
};
