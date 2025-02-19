import { styled } from "styled-components";

import { NotificationBubble } from "./notification-bubble";
import { NotificationBubbleProps } from "./notification-bubble.props";
import { color } from "../../theme";

export default {
  component: NotificationBubble,
  title: "Notification Bubble",
};

const Parent = styled.div`
  background-color: ${color("primaryDisabled")};
  width: 100px;
  height: 100px;
  position: relative;
  border-radius: 10px;
`;

export const primary = (args: NotificationBubbleProps): React.ReactNode => (
  <Parent>
    <NotificationBubble {...args} />
  </Parent>
);
primary.args = {
  notifications: 5,
};
