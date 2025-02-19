import React from "react";
import { styled } from "styled-components";

import { Text } from "../text";
import { ErrorNotificationProps } from "./error-notification.props";
import { color, fontSize, fontWeight, radius, zIndex } from "../../theme";
import { InvisibleButton } from "../button";
import { iconColor } from "../icon/icon";

const Container = styled.div.withConfig({
  shouldForwardProp: (prop) => prop.toString() !== "isShown",
})<Pick<ErrorNotificationProps, "isShown">>`
  background-color: ${color("red")};
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 12px 20px;
  border-radius: ${radius("default")};
  width: 240px;
  position: relative;
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
  opacity: ${({ isShown }) => (isShown ? 1 : 0)};
  transform: ${({ isShown }) =>
    isShown ? "translateY(0)" : "translateY(-10px)"};
  pointer-events: ${({ isShown }) => (isShown ? "auto" : "none")};
  z-index: ${zIndex("notification")};
`;

const TitleText = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h6")};
  font-weight: ${fontWeight("bold")};
`;

const DescriptionText = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h6")};
  margin-top: 4px;
`;

const CloseIcon = styled(InvisibleButton)`
  top: 10px;
  right: 10px;
  position: absolute;
  height: auto;

  .icon {
    ${iconColor("onPrimary")}
  }
`;

export const ErrorNotification: React.FC<ErrorNotificationProps> = ({
  isShown = false,
  title,
  titleTx,
  titleComponents,
  titleData,
  description,
  descriptionTx,
  descriptionComponents,
  descriptionData,
  onClose,
  ...rest
}) => {
  return (
    <Container isShown={isShown} {...rest}>
      {(title ?? titleTx) && (
        <TitleText
          text={title}
          tx={titleTx}
          txComponents={titleComponents}
          txData={titleData}
        />
      )}
      {(description ?? descriptionTx) && (
        <DescriptionText
          text={description}
          tx={descriptionTx}
          txComponents={descriptionComponents}
          txData={descriptionData}
        />
      )}
      <CloseIcon icon="close" onPress={onClose} />
    </Container>
  );
};

export const SuccessNotification = styled(ErrorNotification)`
  background: ${color("green")};
`;
