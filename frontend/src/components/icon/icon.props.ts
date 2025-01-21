import type React from "react";

import type * as icons from "./icons";
import type { Theme } from "../../theme";
import type { UIStateProps } from "../types";

export type IconType = keyof typeof icons;

export interface IconProps extends React.SVGProps<SVGSVGElement>, UIStateProps {
  icon: IconType;
  color?: keyof Theme["colors"];

  /** If set to `true`, displays a small icon. */
  isSmall?: boolean;
}
