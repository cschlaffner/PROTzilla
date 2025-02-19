import type React from "react";

import {
  I18nComponents,
  I18nData,
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps,
} from "../types";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface DropdownOptionProps<T = any> extends I18nLabelProps {
  /**
   * The value of the option. Used for identification.
   * Additionally, if no label is given, the value is displayed as the option text.
   */
  value: T;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface DropdownProps<T = any>
  extends I18nLabelProps,
    I18nPlaceholderProps,
    UIStateProps,
    Omit<React.HTMLAttributes<HTMLDivElement>, "defaultValue" | "onChange"> {
  /** The options from which to select in the drop down. */
  options: DropdownOptionProps<T>[];

  /**
   * The value of the default option to select if no `value` for the current
   * selection is given.
   */
  defaultValue?: T;

  /** The value of the currently selected option. */
  value?: T;

  /**
   * If provided, this handler will be called when the selected option changes.
   */
  onChange?: (value: T) => void;

  /**
   * Whether or not to allow setting a custom other option in addition to the
   * provided options.
   * Defaults to `false`.
   */
  isOtherAllowed?: boolean;

  /**
   * Whether or not the other option is selected.
   * Defaults to `false`.
   */
  isOtherSelected?: boolean;

  /** If set to `true`, displays a small dropdown. */
  isSmall?: boolean;

  /**
   * If provided, this handler will be called when an other option is added via
   * the input text field.
   */
  onOtherChange?: (value: T) => void;

  /** The default option to display as a value in the input text field. */
  defaultOther?: string;

  /** The label to display next to the other option text field. */
  otherLabelTx?: string;

  otherLabelComponents?: I18nComponents;

  otherLabelData?: I18nData;

  /**
   * Whether the drop down should be searchable.
   * Defaults to `false`.
   */
  isSearchable?: boolean;

  /**
   * If provided, this handler will be called on each change of the search
   * input value.
   */
  onSearch?: (value: string) => void;

  /**
   * If provided, a marquee effect will be applied to every option
   * that has more characters than this number
   */
  marqueeTextLength?: number;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface DropdownOptionsProps<T = any>
  extends Pick<
      DropdownProps<T>,
      | "options"
      | "isOtherSelected"
      | "isSmall"
      | "isDisabled"
      | "isOtherAllowed"
      | "onOtherChange"
      | "otherLabelTx"
      | "otherLabelComponents"
      | "otherLabelData"
      | "marqueeTextLength"
    >,
    Omit<React.HTMLAttributes<HTMLDivElement>, "defaultValue"> {
  activeOptionIndex?: number;

  setValue: (newValue: T, shouldCloseOnChange?: boolean) => void;

  other: string;

  setOther: (value: T) => void;

  anchor?: HTMLElement | null;
}
