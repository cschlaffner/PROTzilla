import { Color } from "@protzilla/theme";
import { UIStateProps } from "@protzilla/utils";
import type React from "react";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface ISwitchOption<T = any> extends UIStateProps {
  /**
   * The value of the option. Used for identification.
   * Additionally, if no label is given, the value is displayed as the option text.
   *
   */
  label?: string;
  value: T;
  color?: Color;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface SwitchProps<T = any>
  extends UIStateProps,
    Omit<React.HTMLAttributes<HTMLDivElement>, "defaultValue" | "onChange"> {
  label?: string;
  /** The options from which to select in the drop down. */
  options: ISwitchOption<T>[];

  /** The value of the currently selected option. */
  value?: T;

  /** The default value which is used if no value is provided. */
  defaultValue?: T;

  /**
   * If provided, this handler will be called when the selected option changes.
   */
  onChange?: (value: T) => void;
}
