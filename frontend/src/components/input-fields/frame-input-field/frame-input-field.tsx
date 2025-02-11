import React, { useRef } from "react";
import { FrameInputFieldProps } from "./frame-input-field.props";
import { InputLabel, Text } from "../../text";
import styled from "styled-components";
import { fontSize, spacing, border, borderColors, color } from "../../../theme";

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 0px ${spacing("verySmall")};
  padding: ${spacing("verySmall")} 0px;
  max-width: 500px;
`;

const GridItem = styled.div<{ row: number; col: number }>`
  grid-row: ${({ row }) => row};
  grid-column: ${({ col }) => col};
`;

const FlexContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: ${spacing("verySmall")};
  width: 100%;
`;

const StyledInputFrame = styled.div`
  border: ${border("defaultStrength")} solid ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  background-color: white;
  display: flex;
  gap: ${spacing("verySmall")};
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
  width: 100%;
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
  display: flex;
  align-items: center;
  gap: ${spacing("verySmall")};
  cursor: pointer;
  width: 100%;
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

const StyledSubtitle = styled(Text)`
  font-size: ${fontSize("small")};
  margin: ${spacing("verySmall")} 0 0 0;
  color: ${color("gray50")};
  padding: 0 ${spacing("verySmall")};
`;

const StyledSubscriptText = styled(StyledSubtitle)`
  white-space: normal;
  word-break: break-word;
  flex: 1;
`;

const FixedText = styled(StyledSubtitle)`
  flex-shrink: 0;
  margin-left: 8px;
  font-style: italic;
`;

const getChildStyle = () => ({
  padding: "10px",
  border: "none",
  outline: "none",
  background: "transparent",
  width: "100%",
});

export const FrameInputField: React.FC<FrameInputFieldProps> = ({
  label,
  labelPosition = "top",
  subscript,
  optional = false,
  children,
  inlinePrefix,
  inlineSuffix,
  separatePrefix,
  separateSuffix,
}) => {
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
    <GridContainer>
      {labelPosition === "top" ? (
        <GridItem row={1} col={2}>
          {label && (
            <InputLabel
              className="label"
              text={label}
              style={{ padding: "0 5px" }}
            />
          )}
        </GridItem>
      ) : (
        <GridItem row={2} col={1}>
          {label && (
            <InputLabel
              className="label"
              text={label + ":"}
              style={{ padding: "0 10px" }}
            />
          )}
        </GridItem>
      )}
      <GridItem row={2} col={2}>
        <StyledInputFrame>
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
          {subscript && (
            <StyledSubscriptText
              className="subscript"
              text={subscript}
              style={{ whiteSpace: "normal" }}
            />
          )}
          {optional && <FixedText text="optional" />}
        </FlexContainer>
      </GridItem>
    </GridContainer>
  );
};
