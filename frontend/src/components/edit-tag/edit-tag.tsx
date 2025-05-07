import React from "react";
import { css, styled } from "styled-components";

import { color, fontSize, fontWeight, opacity } from "../../theme";
import { FlexRow } from "../box";
import { InvisibleButton } from "../button";
import { iconColor } from "../icon";
import { Text } from "../text";
import { EditTagProps } from "./edit-tag.props";
import { UIStateProps } from "../types";

const Container = styled(FlexRow)<UIStateProps>`
  background-color: ${color("secondary")};
  -webkit-tap-highlight-color: transparent;
  align-items: center;
  height: 20px;
  justify-content: center;
  box-sizing: border-box;
  border-radius: 11px;
  padding: 4px 10px 4px 16px;
  max-width: 100%;

  ${(props) =>
    props.isDisabled &&
    css`
      opacity: ${opacity("disabled")};
    `}
`;

const StyledText = styled(Text)`
  font-size: ${fontSize("small")};
  font-weight: ${fontWeight("bold")};
  line-height: 12px;
  margin-right: 3px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
`;

const StyledButton = styled(InvisibleButton)`
  height: unset;
  min-height: unset;

  .icon {
    ${iconColor("text")}
  }
`;

export const EditTag: React.FC<EditTagProps> = ({
  icon = "close",
  text,
  tx,
  txComponents,
  txData,
  onButtonPress,
  isDisabled,
  ...rest
}) => (
  <Container {...rest}>
    {(tx ?? text) && (
      <StyledText
        className="text"
        text={text}
        tx={tx}
        txComponents={txComponents}
        txData={txData}
        isDisabled={isDisabled}
      />
    )}

    <StyledButton className="icon" icon={icon} onPress={onButtonPress} isDisabled={isDisabled} />
  </Container>
);
