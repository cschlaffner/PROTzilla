import React, { useEffect, useState } from "react";
import { styled } from "styled-components";

import { Text } from "../text";
import { color, fontSize, fontWeight, radius, zIndex } from "../../theme";
import { InvisibleButton } from "../button";
import { iconColor } from "../icon/icon";
import { NotificationProps } from "./notification.props";

const Container = styled.div<{ isShown: boolean, type: string  }>`
  background-color: ${({ type }) =>
    type === "error" ? color("red") : (type === "success" ? color("green") : (type === "warning" ? color("yellow") : color("blue")))};
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

export const Notification: React.FC<NotificationProps> = ({
  title,
  message,
  type = 'error',
  isShown: propIsShown = false,
  closeable = true,
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
      {(title) && (
        <TitleText
          text={title}
        />
      )}
      {(message) && (
        <DescriptionText
          text={message}
        />
      )}
      {isShown && closeable && <CloseIcon icon="close" onPress={handleClose} />}
    </Container>
  );
};
