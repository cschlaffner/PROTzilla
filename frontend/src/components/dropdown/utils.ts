import React from "react";

import { useRelativePosition } from "../../hooks";

export interface RelativePositionConfig {
  /** The anchor element or position. */
  anchor?: HTMLElement | null;

  /**
   * If set to `true`, the position is actively updated.
   * Defaults to `true`.
   */
  isActive?: boolean;

  /**
   * The positioned element's distance to its parent.
   * Defaults to a value based on the current theme.
   */
  distance?: number;
}

export interface RelativePositionStyleConfig extends Pick<RelativePositionConfig, "distance"> {
  /** The parent element's bounding client rect. */
  rect: DOMRect;

  /** The offset parent's bounding client rect (if any). */
  offsetRect?: DOMRect;
}

const computeStyle = ({ rect, distance }: RelativePositionStyleConfig): React.CSSProperties => ({
  position: "absolute",
  top: rect.top + rect.height + (distance ?? 0),
  left: rect.left,
  right: document.body.getBoundingClientRect().width - rect.right,
});

/**
 * Returns a style object that absolutely positions the options of a drop down
 * menu.
 */
export const useFloatingPosition = (config: RelativePositionConfig): React.CSSProperties =>
  useRelativePosition(computeStyle, config);
