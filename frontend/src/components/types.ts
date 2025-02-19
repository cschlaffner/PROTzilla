import type React from "react";

/** Additional data, passed to the translation function. */
export interface I18nData {
  context?: string;
  count?: number;
  date?: Date;
  [key: string]: unknown;
}

export type I18nComponents =
  | readonly React.ReactElement[]
  | Readonly<Record<string, React.ReactElement>>;

export interface I18nProps {
  /** The raw text (is preceeded by `tx`, preceedes `children`). */
  text?: React.ReactNode;

  /** The key for i18n translation (preceeds `text` & `children`). */
  tx?: string;

  /**
   * Optional components to be used to style the translated text when `tx`
   * is being used.
   */
  txComponents?: I18nComponents;

  /**
   * Additional data, passed to the translation function when `tx` is being
   * used.
   */
  txData?: I18nData;
}

export interface I18nLabelProps {
  /** The raw label text (is preceeded by `labelTx`). */
  label?: React.ReactNode;

  /**
   * The key for i18n translation of the label (preceeds `label`).
   */
  labelTx?: string;

  /**
   * Optional components to be used to style the translated label text when
   * `labelTx` is being used.
   */
  labelComponents?: I18nComponents;

  /**
   * Additional data, passed to the label translation function when `labelTx`
   * is being used.
   */
  labelData?: I18nData;
}

export interface I18nTitleProps {
  /** The raw title text (is preceeded by `titleTx`). */
  title?: React.ReactNode;

  /**
   * The key for i18n translation of the title (preceeds `title`).
   */
  titleTx?: string;

  /**
   * Optional components to be used to style the translated title text when
   * `titleTx` is being used.
   */
  titleComponents?: I18nComponents;

  /**
   * Additional data, passed to the title translation function when `titleTx`
   * is being used.
   */
  titleData?: I18nData;
}
export interface I18nDescriptionProps {
  /** The raw text of the description (is preceeded by `descriptionTx`). */
  description?: React.ReactNode;

  /**
   * The key for i18n translation of the description (preceeds `description`).
   */
  descriptionTx?: string;

  /**
   * Optional components to be used to style the translated description when
   * `descriptionTx` is being used.
   */
  descriptionComponents?: I18nComponents;

  /**
   * Additional data, passed to the translation function for the description
   * when `descriptionTx` is being used.
   */
  descriptionData?: I18nData;
}

export interface I18nActionProps {
  /** The raw text of the action (is preceeded by `actionTx`). */
  action?: React.ReactNode;

  /** The key for i18n translation of the action (preceeds `action`). */
  actionTx?: string;

  /**
   * Optional components to be used to style the translated description when
   * `actionTx` is being used.
   */
  actionComponents?: I18nComponents;

  /**
   * Additional data, passed to the translation function for the description
   * when `actionTx` is being used.
   */
  actionData?: I18nData;
}

export interface I18nPlaceholderProps {
  /** The raw placeholder text (is preceeded by `placeholderTx`). */
  placeholder?: string;

  /**
   * The key for i18n translation of the placeholder (preceeds `placeholder`).
   */
  placeholderTx?: string;

  /**
   * Additional data, passed to the placeholder translation function when
   * `placeholderTx` is being used.
   */
  placeholderData?: I18nData;
}

export type I18nMessage = I18nTitleProps & I18nDescriptionProps;

export interface UIStateProps {
  isDisabled?: boolean;
}
