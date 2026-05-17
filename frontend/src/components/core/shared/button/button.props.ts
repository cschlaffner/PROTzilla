import { GridFilterModel, GridSortModel } from "@mui/x-data-grid";
import type { Color } from "@protzilla/theme";
import type { UIStateProps } from "@protzilla/utils";
import type React from "react";

import type { IconType } from "../icon";
import type { TooltippedProps } from "../tooltip";

export interface ButtonRef extends HTMLButtonElement {
  /** Forces to hide the focus indicator for the subsequent focus event. */
  hideFocus(): void;
}

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    TooltippedProps,
    UIStateProps {
  /** The key of the button's icon (if any). */
  icon?: IconType;
  color?: Color;
  /** Position of icon left of text or Right of text default to Left */
  iconRight?: boolean;
  /**
   * The key of the button's icon for the pressed state (if any).
   * Setting this will override the main icon while the button is pressed.
   */
  pressedIcon?: IconType;

  text?: string;
  tag?: string;
  tagTx?: string;

  textStyle?: React.CSSProperties;

  /** If set to `true`, hides the background color unless interacted with. */
  isShy?: boolean;

  /** If set to `true`, displays a small button. */
  isSmall?: boolean;

  /** If set to `true`, displays a big button. */
  isBig?: boolean;

  /** If set to `true`, overrides the hover and active color to cautious. */
  isCautious?: boolean;

  /** If set to `true`, skips the tooltip delay. */
  showTooltipImmediately?: boolean;

  /**
   * Indicates whether the focus outline should be shown. Setting this to
   * `false` suppresses it.
   */
  showFocusOutline?: boolean;

  /**
   * An event listener that fires when the button is pressed using a pointer
   * device or activated using the keyboard.
   */
  onPress?: (
    event: React.PointerEvent<HTMLButtonElement> | React.KeyboardEvent<HTMLButtonElement>,
  ) => void;
}

export interface ToggleableButtonProps extends ButtonProps {
  isActive?: boolean;
}

export interface StatusButtonProps extends ButtonProps {
  isLoading?: boolean;
  isDone?: boolean;
}

export interface CSVButtonProps extends ButtonProps {
  runName: string;
  tableLabel: string;
  fileName?: string;
  sortModel: GridSortModel;
  filterModel: GridFilterModel;
}
