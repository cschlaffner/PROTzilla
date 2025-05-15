import type { Color } from "@protzilla/theme";
import type { UIStateProps } from "@protzilla/utils";
import type React from "react";

import type * as icons from "./icons";

export type IconType = keyof typeof icons;
export type DefaultColoredIconType = "complete" | "incomplete" | "failed" | "outdated";

export interface IconProps extends React.SVGProps<SVGSVGElement>, UIStateProps {
  icon: IconType;
  color?: Color;

  /** If set to `true`, displays a different sized icon. */
  isSmall?: boolean;
  isBig?: boolean;
}

export interface DefaultColoredIconProps extends React.SVGProps<SVGSVGElement>, UIStateProps {
  icon: DefaultColoredIconType;
  isSmall?: boolean;
  isBig?: boolean;
}

export interface IconButtonProps extends IconProps {
  hoverColor?: Color;
}
