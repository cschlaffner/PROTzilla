import React from "react";
import { styled } from "styled-components";

import { Text } from "../text";
import { NotificationBubbleProps } from "./notification-bubble.props";
import { color, fontWeight } from "../../theme";

const Bubble = styled.div<Pick<NotificationBubbleProps, "color">>`
  align-items: center;
  background: ${(props) => color(props.color ?? "red")};
  border-radius: 50%;
  display: flex;
  height: 16px;
  justify-content: center;
  position: absolute;
  right: -8px;
  top: -8px;
  width: 16px;
`;

const NotificationText = styled(Text)`
  color: ${color("onPrimary")};
  font-size: 9px;
  font-weight: ${fontWeight("bold")};
  line-height: 9px;
`;

export const NotificationBubble: React.FC<NotificationBubbleProps> = ({
  notifications,
  ...rest
}) =>
  notifications ? (
    <Bubble {...rest}>
      {typeof notifications === "number" && (
        <NotificationText className="notification-text" text={Math.min(notifications, 9)} />
      )}
    </Bubble>
  ) : null;
