import type React from "react";

import type { Theme } from "../../theme";

export interface NotificationBubbleProps
  extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * The amount of notifications (capped to `9`) or a flag whether or not
   * notifications ar present.
   */
  notifications?: boolean | number;

  /**
   * The color of the notification bubble.
   * Defaults to `"red"`.
   */
  color?: keyof Theme["colors"];
}
