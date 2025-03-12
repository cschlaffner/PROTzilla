import type React from "react";

import type { ISwitchOption } from "./switch.props";
import { Color } from "../../theme";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface SwitchOptionProps<T = any>
  extends ISwitchOption<T>,
    React.HTMLAttributes<HTMLButtonElement> {
  isActive?: boolean;
  color?: Color
}
