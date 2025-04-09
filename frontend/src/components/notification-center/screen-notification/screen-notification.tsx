import React, { useEffect, useState } from "react";
import { styled } from "styled-components";

import { ScreenNotificationProps } from "./screen-notification.props";
import {
  color,
  fontSize,
  fontWeight,
  radius,
  size,
  spacing,
  zIndex,
} from "../../../theme";
import { FlexColumn, FlexRow } from "../../box";
import { InvisibleButton } from "../../button";
import { iconColor } from "../../icon/icon";
import { Text } from "../../text";

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
  width: 100%;
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
  width: 100%;
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
  width: ${size("buttonHeight")};

  .icon {
    ${iconColor("onPrimary")}
  }
`;

export const ScreenNotification: React.FC<ScreenNotificationProps> = ({
  title,
  message,
  type = "error",
  isShown: propIsShown = false,
  closeAfterMs = -1,
  onClose,
  ...props
}) => {
  const [isShown, setIsShown] = useState(propIsShown);

  useEffect(() => {
    if (isShown && closeAfterMs > 0) {
      const timer = setTimeout(() => {
        setIsShown(false);
        onClose?.();
      }, closeAfterMs);

      return () => {
        clearTimeout(timer);
      };
    }
  }, [isShown, closeAfterMs, onClose]);

  const handleClose = () => {
    setIsShown(false);
    onClose?.();
  };

  return (
    <Container isShown={isShown} type={type} {...props}>
      <TextContainer>
        {title && <TitleText text={title} />}
        {message && <DescriptionText text={message} />}
      </TextContainer>
      {isShown && <CloseIcon icon="close" onPress={handleClose} isShy />}
    </Container>
  );
};
