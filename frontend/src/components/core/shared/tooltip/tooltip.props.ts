import type React from "react";

import type { TooltipPosition, TooltipPositionConfig } from "./utils";

export interface TooltipProps
  extends React.HTMLAttributes<HTMLDivElement>,
    Pick<TooltipPositionConfig, "anchor" | "position" | "distance"> {
  /** The z-index of the surface below. */
  baseZIndex?: number;
  isShown?: boolean;
  text?: string;
}

export interface TooltippedProps {
  /**
   * Indicates whether the tooltip should be shown. Setting this to `false`
   * suppresses it.
   */
  showTooltip?: boolean;

  // Tooltip Content

  /** The raw tooltip text */
  tooltip?: string;

  // Tooltip Positioning

  /**
   * Indicates if the tooltip should be positioned relative to its parent
   * element or the mouse cursor.
   *
   * Defaults to `true`.
   */
  anchorTooltipToMouse?: boolean;

  /**
   * The position of the tooltip relative to either its parent element or mouse
   * cursor (depending on `anchorTooltipToMouse`).
   */
  tooltipPosition?: TooltipPosition;

  /**
   * The tooltip's distance from either its parent element or mouse cursor
   * (depending on `anchorTooltipToMouse`).
   */
  tooltipDistance?: number;

  /**
   * The position of the tooltip relative to its parent element when it is
   * shown because its parent element receives keyboard focus.
   */
  tooltipPositionFocus?: TooltipPosition;

  /**
   * The tooltip's distance from either its parent element when it is shown
   * because its parent element receives keyboard focus.
   */
  tooltipDistanceFocus?: number;
}
