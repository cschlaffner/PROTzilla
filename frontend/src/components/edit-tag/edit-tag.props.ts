import type React from "react";

import type { IconType } from "../icon";
import { I18nProps, UIStateProps } from "../types";

export interface EditTagProps
  extends React.HTMLAttributes<HTMLDivElement>,
    I18nProps,
    UIStateProps {
  /** The key of the button's icon. Defaults to `"cross"`. */
  icon?: IconType;

  onButtonPress?: () => void;
}
