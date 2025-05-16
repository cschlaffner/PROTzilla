import { color, fontSize, fontWeight, radius, size, spacing, zIndex } from "@protzilla/theme";
import React, { useEffect, useState } from "react";
import { styled, useTheme } from "styled-components";

import { ScreenNotificationProps } from "./screen-notification.props";
import { FlexColumn, FlexRow , GrayButton , iconColor , Text } from "../../../core/";




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
  transform: ${({ isShown }) => (isShown ? "translateY(0)" : "translateY(-10px)")};
  pointer-events: ${({ isShown }) => (isShown ? "auto" : "none")};
  z-index: ${zIndex("notification")};
  position: relative;
  overflow: hidden;
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

const CloseIcon = styled(GrayButton)`
  width: ${size("buttonHeight")};

  .icon {
    ${iconColor("onPrimary")}
  }
`;

const ProgressBar = styled.div<{ active: boolean; duration: number }>`
  position: absolute;
  bottom: 0;
  left: 0;
  height: ${spacing("verySmall")};
  background-color: rgba(255, 255, 255, 0.5);
  width: ${({ active }) => (active ? "100%" : "0%")};
  transition: width ${({ duration }) => duration}ms linear;
  border-radius: ${radius("default")};
`;

export const ScreenNotification: React.FC<ScreenNotificationProps> = ({
  title,
  message,
  type = "error",
  isShown: propIsShown = false,
  isClosingAutomatically = true,
  closeAfterMs: closeAfterMsProp = -1,
  onClose,
  ...props
}) => {
  const [isShown, setIsShown] = useState(propIsShown);
  const theme = useTheme();
  const closeAfterMs =
    closeAfterMsProp > 0 ? closeAfterMsProp : theme.durations.standardNotificationDuration;
  const [hasStartedProgressBar, setHasStartedProgressBar] = useState(false);

  useEffect(() => {
    if (isShown && isClosingAutomatically && closeAfterMs > 0) {
      setHasStartedProgressBar(true);

      const timer = setTimeout(() => {
        setIsShown(false);
        onClose?.();
      }, closeAfterMs);

      return () => {
        clearTimeout(timer);
        setHasStartedProgressBar(false);
      };
    }
  }, [isShown, isClosingAutomatically, closeAfterMs, onClose]);

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
      {isClosingAutomatically && closeAfterMs > 0 && (
        <ProgressBar active={hasStartedProgressBar} duration={closeAfterMs} />
      )}
    </Container>
  );
};
