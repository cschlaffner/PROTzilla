import React, { useEffect, useState } from "react";
import { styled, useTheme } from "styled-components";

import { ScreenNotificationProps } from "./screen-notification.props";
import { color, fontSize, fontWeight, radius, size, spacing, zIndex } from "../../../theme";
import { FlexColumn, FlexRow } from "../../box";
import { GrayButton } from "../../button";
import { iconColor } from "../../icon";
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
  max-width: 100%;
  align-items: flex-start;
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
  flex: 1;
  min-width: 0;
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
  flex-shrink: 0;
  margin-left: ${spacing("small")};

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

const TracebackContainer = styled(FlexColumn)`
  width: 100%;
  gap: ${spacing("verySmall")};
  margin-top: ${spacing("small")};
`;

const TracebackToggle = styled(GrayButton)`
  font-weight: ${fontWeight("bold")};
  color: ${color("onPrimary")};
  text-align: left;
  padding: ${spacing("verySmall")};
  background: none;
  border: none;
  cursor: pointer;
`;

const TracebackText = styled(Text)`
  color: ${color("onPrimary")};
  font-size: ${fontSize("h6")};
  word-wrap: break-word;
  overflow-wrap: break-word;
  width: 100%;
  white-space: pre-wrap;
`;

export const ScreenNotification: React.FC<ScreenNotificationProps> = ({
  title,
  message,
  traceback,
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
  const [isTracebackVisible, setIsTracebackVisible] = useState(false);

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

  const toggleTracebackVisibility = () => {
    setIsTracebackVisible((prev) => !prev);
  };

  return (
    <Container isShown={isShown} type={type} {...props}>
      <TextContainer>
        {title && <TitleText text={title} />}
        {message && <DescriptionText text={message} />}
        {traceback && (
          <TracebackContainer>
            <TracebackToggle onClick={toggleTracebackVisibility}>
              {isTracebackVisible ? "Hide Traceback" : "Show Traceback"}
            </TracebackToggle>
            {isTracebackVisible && <TracebackText text={traceback} />}
          </TracebackContainer>
        )}
      </TextContainer>
      {isShown && <CloseIcon icon="close" onPress={handleClose} isShy />}
      {isClosingAutomatically && closeAfterMs > 0 && (
        <ProgressBar active={hasStartedProgressBar} duration={closeAfterMs} />
      )}
    </Container>
  );
};
