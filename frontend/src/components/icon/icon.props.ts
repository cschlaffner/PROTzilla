import type React from "react";

import type * as icons from "./icons";
import type { Theme } from "../../theme";
import type { UIStateProps } from "../types";

export type IconType = keyof typeof icons;
export type defaultColoredIconType = "complete"|"incomplete"|"failed"|"outdated";
export type Color = keyof Theme["colors"]

export interface IconProps extends React.SVGProps<SVGSVGElement>, UIStateProps {
  icon: IconType;
  color?: Color;

  /** If set to `true`, displays a small icon. */
  isSmall?: boolean;
}

export interface defaultColoredIconProps extends React.SVGProps<SVGSVGElement>, UIStateProps {
  icon: defaultColoredIconType;
  isSmall?: boolean;
}

