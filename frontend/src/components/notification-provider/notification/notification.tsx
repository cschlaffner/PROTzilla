import React, { useEffect, useState } from "react";
import { styled } from "styled-components";

import { Text } from "../../text";
import {
  color,
  fontSize,
  fontWeight,
  radius,
  spacing,
  zIndex,
} from "../../../theme";
import { InvisibleButton } from "../../button";
import { iconColor } from "../../icon/icon";
import { NotificationProps } from "./notification.props";
import { FlexColumn, FlexRow } from "../../box";

const Container = styled(FlexRow)<{ isShown: boolean; type: string }>`
  background-color: ${({ type }) =>
    type === "error"
      ? color("protzillaRed")
      : type === "success"
        ? color("green")
        : type === "warning"
          ? color("protzillaDarkBlue")
          : color("gray50")};
  padding: ${spacing("small")};
  border-radius: ${radius("default")};
  width: 200px;
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
  opacity: ${({ isShown }) => (isShown ? 1 : 0)};
  transform: ${({ isShown }) =>
    isShown ? "translateY(0)" : "translateY(-10px)"};
  pointer-events: ${({ isShown }) => (isShown ? "auto" : "none")};
  z-index: ${zIndex("notification")};
`;

const TextContainer = styled(FlexColumn)`
  width: 85%;
  gap: ${spacing("verySmall")};
`;

const TitleText = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h6")};
  font-weight: ${fontWeight("bold")};
  word-wrap: break-word;
  overflow-wrap: break-word;
  width: 100%;
`;

const DescriptionText = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h6")};
  word-wrap: break-word;
  overflow-wrap: break-word;
  width: 100%;
`;

const CloseIcon = styled(InvisibleButton)`
  width: 15%;

  .icon {
    ${iconColor("onPrimary")}
  }
`;

export const Notification: React.FC<NotificationProps> = ({
  title,
  message,
  type = "error",
  isShown: propIsShown = false,
  closeAfterMs = -1,
  onClose,
  ...rest
}) => {
  const [isShown, setIsShown] = useState(propIsShown);

  useEffect(() => {
    if (isShown && closeAfterMs > 0) {
      const timer = setTimeout(() => {
        setIsShown(false);
        onClose?.();
      }, closeAfterMs);

      return () => clearTimeout(timer);
    }
  }, [isShown, closeAfterMs, onClose]);

  const handleClose = () => {
    setIsShown(false);
    onClose?.();
  };

  return (
    <Container isShown={isShown} type={type} {...rest}>
      <TextContainer>
        {title && <TitleText text={title} />}
        {message && <DescriptionText text={message} />}
      </TextContainer>
      {isShown && <CloseIcon icon="close" onPress={handleClose} isShy />}
    </Container>
  );
};
