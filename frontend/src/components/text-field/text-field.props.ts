import type {
  I18nComponents,
  I18nData,
  I18nLabelProps,
  I18nPlaceholderProps,
  UIStateProps,
} from "../types";

export interface TextFieldProps
  extends Omit<
      React.InputHTMLAttributes<HTMLInputElement>,
      "defaultValue" | "value"
    >,
    I18nLabelProps,
    I18nPlaceholderProps,
    UIStateProps {
  defaultValue?: string;
  value?: string;

  /**
   * The key for i18n translation of the value (preceeds `value`).
   */
  valueTx?: string;

  /**
   * Additional data, passed to the value translation function when
   * `valueTx` is being used.
   */
  valueData?: I18nData;

  hasSuccess?: boolean;
  hasError?: boolean;

  /**
   * Whether or not this input is required.
   * Only renders when a label is rendered.
   * Defaults to `false`.
   */
  isRequired?: boolean;

  /**
   * Whether or not this input is optional. Is preceeded by `isRequired`.
   * Only renders when a label is rendered.
   * Defaults to `false`.
   */
  isOptional?: boolean;

  /**
   * Text displayed below the text field.
   * Is superceeded by `subscriptTx` and `maxTags` if `type` is `tag`.
   */
  subscript?: string;

  /**
   * Translation key for text displayed below the text field.
   * Is superceeded by `maxTags` if `type` is `tag`.
   */
  subscriptTx?: string;

  /**
   * Optional components to be used to style the translated text when
   * `subscriptTx` is being used.
   */
  subscriptComponents?: I18nComponents;

  /**
   * Additional data, passed to the translation function when `subscriptTx` is
   * being used.
   */
  subscriptData?: I18nData;

  /** A callback that is called when the value is changed. */
  onChangeText?: (value: string) => void;

  /** A callback that is called when the changed value is confirmed. */
  onConfirm?: (value: string) => void;

  /** A callback that is called when the changed value is discarded. */
  onCancel?: (value: string) => void;

  /**
   * A callback that is called when the text field is submitted using the
   * `Enter` key.
   *
   * This listener is fired after the `onConfirm` callback, if one is defined.
   */
  onSubmitField?: () => void;

  /** Optional limit for character count. */
  maxCharacters?: number;

  /**
   * Optional custom key for i18n translation of the character limit text.
   * Receives `{ currentLength: number; maxLength: number; }` as `txData`.
   */
  maxCharactersTx?: string;

  /**
   * The tags shown when `kind` = `"tag"`.
   */
  tags?: string[];

  /**
   * Setter for the tags shown when `kind` = `"tag"`.
   */
  setTags?: (tags: string[]) => void;

  /** Optional limit for tag count. */
  maxTags?: number;

  /**
   * Optional custom key for i18n translation of the tag limit text.
   * Receives `{ currentLength: number; maxLength: number; }` as `txData`.
   */
  maxTagsTx?: string;

  /**
   * An optional transformation function for tags entered by the user.
   * Only applies when `kind` = `"tag"`.
   */
  tagTransformFunction?: (value: string) => string;
}

export interface MultilineTextFieldProps extends TextFieldProps {
  /**
   * Restricts the width of the text area to the provided value.
   * Accepts `string`, thus a unit has to be provided (e.g., width='20vw').
   * If no `width` is provided, the `min-width` is set to `100px`.
   */
  width?: string;

  /**
   * Restricts the height of the text area to the provided value.
   * Accepts `string`, thus a unit has to be provided (e.g., height='200px').
   * By default the `height` is not restricted at all.
   */
  height?: string;
}

export interface CollapsibleLabelProps {
  width: number | string;
  collapsedWidth?: number;
  isCollapsed: boolean;
  children?: React.ReactNode;
}
