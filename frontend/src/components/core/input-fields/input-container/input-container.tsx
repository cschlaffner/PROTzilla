import { InfoIComponent, InputLabel, Text } from "@protzilla/core";
import { border, borderColors, color, fontSize, spacing, styledDiv } from "@protzilla/theme";
import React, { useRef } from "react";
import { styled, useTheme } from "styled-components";

import { InputContainerProps } from "./input-container.props";

const GridContainer = styledDiv.div`
  align-items: center;
  display: grid;
  grid-template-columns: auto 1fr;
  padding: ${spacing("verySmall")} 0px;
`;

const GridItem = styledDiv.div<{ row: number; col: number }>`
  grid-column: ${({ col }) => col};
  grid-row: ${({ row }) => row};
`;

const FlexContainer = styledDiv.div`
  align-items: flex-start;
  display: flex;
  gap: ${spacing("verySmall")};
  justify-content: space-between;
  width: 100%;
`;

const StyledInputFrame = styled.div.withConfig({
  shouldForwardProp: (prop: string) => prop.toString() !== "smallBorder",
})<{ smallBorder: boolean }>`
  box-sizing: border-box;
  background-color: ${color("transparent")};
  border: ${({ smallBorder }) => border(smallBorder ? "smallStrength" : "defaultStrength")} solid
    ${borderColors("default")};
  border-radius: ${border("defaultRadius")};
  display: flex;
  gap: ${spacing("verySmall")};
  width: 100%;
`;

const StyledSeparateAffix = styledDiv.div`
  align-items: center;
  background: ${color("gray6")};
  box-sizing: content-box;
  display: flex;
  font-size: ${fontSize("default")};
  padding: 0px ${spacing("verySmall")};
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

const StyledInputContainer = styledDiv.div`
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

const LabelContainer = styled.div`
  align-items: start;
  display: flex;
  gap: ${spacing("verySmall")};
  width: 100%;
`;

export const InputContainer: React.FC<InputContainerProps> = ({
  children,
  label,
  labelPosition = "top",
  info,
  optional = false,
  subscript,
  inlinePrefix,
  inlineSuffix,
  separatePrefix,
  separateSuffix,
  smallBorder = false,
  ...props
}) => {
  const theme = useTheme();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const handleClick = () => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const styledChildren = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child as React.ReactElement, {
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
            <LabelContainer>
              <InputLabel className="label" text={label} />
              {info && <InfoIComponent text={info} isSmall />}
            </LabelContainer>
          )}
        </GridItem>
      ) : (
        <GridItem row={2} col={1}>
          {label && (
            <LabelContainer style={{ marginRight: theme.spacing.verySmall }}>
              <InputLabel className="label" text={label + ":"} />
              {info && <InfoIComponent text={info} isSmall />}
            </LabelContainer>
          )}
        </GridItem>
      )}
      <GridItem row={2} col={2}>
        <StyledInputFrame smallBorder={smallBorder}>
          {separatePrefix && (
            <StyledSeparatePrefix className="separate-prefix">
              {separatePrefix}
            </StyledSeparatePrefix>
          )}
          <StyledInputContainer onClick={handleClick}>
            {inlinePrefix && (
              <StyledInlinePrefix className="inline-prefix">{inlinePrefix}</StyledInlinePrefix>
            )}
            {styledChildren}
            {inlineSuffix && (
              <StyledInlineSuffix className="inline-suffix">{inlineSuffix}</StyledInlineSuffix>
            )}
          </StyledInputContainer>
          {separateSuffix && (
            <StyledSeparateSuffix className="separate-suffix">
              {separateSuffix}
            </StyledSeparateSuffix>
          )}
        </StyledInputFrame>
      </GridItem>
      {(subscript ?? optional) && (
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
      )}
    </GridContainer>
  );
};
