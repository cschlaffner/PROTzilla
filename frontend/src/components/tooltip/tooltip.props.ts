import type React from "react";

import type { TooltipPosition, TooltipPositionConfig } from "./utils";
import type { I18nComponents, I18nData, I18nProps } from "../types";

export interface TooltipProps
  extends React.HTMLAttributes<HTMLDivElement>,
    I18nProps,
    Pick<TooltipPositionConfig, "anchor" | "position" | "distance"> {
  /** The z-index of the surface below. */
  baseZIndex?: number;

  isShown?: boolean;
}

export interface TooltippedProps {
  /**
   * Indicates whether the tooltip should be shown. Setting this to `false`
   * suppresses it.
   */
  showTooltip?: boolean;

  // Tooltip Content

  /** The raw tooltip text (is preceeded by `tooltipTx`). */
  tooltip?: React.ReactNode;

  /** The key for i18n translation of the tooltip (preceeds `tooltip`). */
  tooltipTx?: string;

  /**
   * Optional components to be used to style the translated tooltip when
   * `tooltipTx` is being used.
   */
  tooltipComponents?: I18nComponents;

  /**
   * Additional data, passed to the tooltip's translation function when
   * `tooltipTx` is being used.
   */
  tooltipData?: I18nData;

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
