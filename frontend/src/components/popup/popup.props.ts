import { IconType } from "../icon";
import type {
  I18nComponents,
  I18nData,
  I18nDescriptionProps,
  I18nProps,
  I18nTitleProps,
} from "../types";
import type { buttonComponents } from "./button-components";

export type PopUpButtonKind = "primary" | "secondary" | "red" | "green";

export interface PopUpProps
  extends I18nProps,
    I18nTitleProps,
    I18nDescriptionProps,
    Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  /**
   * The raw confirm text (is preceeded by a manually set `confirmTx`).
   */
  confirm?: string;

  /**
   * The key for i18n translation of the confirm text.
   * Defaults to `"confirm"`.
   */
  confirmTx?: string;

  /**
   * Optional components to be used to style the translated confirm when
   * `confirmTx` is being used.
   */
  confirmComponents?: I18nComponents;

  /**
   * Additional data, passed to the translation function when `confirmTx` is
   * being used.
   */
  confirmData?: I18nData;

  confirmIcon?: IconType;

  /**
   * The kind up button used for the conform button.
   * Defaults to `"primary"`.
   */
  confirmButtonKind?: keyof typeof buttonComponents;

  /**
   * Whether or not to autofocus the confirm button (preceeds
   * `dismissAutoFocus`).
   * Defaults to `false`.
   */
  confirmAutoFocus?: boolean;

  /**
   * Whether or not the confirm button is disabled.
   * Defaults to `false`.
   */
  isConfirmDisabled?: boolean;

  /**
   * The raw dismiss text (is preceeded by a manually set `dismissTx`).
   */
  dismiss?: string;

  /**
   * The key for i18n translation of the dismiss text.
   * Defaults to `"dismiss"`.
   */
  dismissTx?: string;

  /**
   * Optional components to be used to style the translated dismiss when
   * `dismissTx` is being used.
   */
  dismissComponents?: I18nComponents;

  /**
   * Additional data, passed to the translation function when `dismissTx` is
   * being used.
   */
  dismissData?: I18nData;

  dismissIcon?: IconType;

  /**
   * The kind up button used for the conform button.
   * Defaults to `"primary"`.
   */
  dismissButtonKind?: keyof typeof buttonComponents;

  /**
   * Whether or not to autofocus the dismiss button (is preceeded by
   * `confirmAutoFocus`).
   * Defaults to `false`.
   */
  dismissAutoFocus?: boolean;

  /**
   * Whether or not the dismiss button is disabled.
   * Defaults to `false`.
   */
  isDismissDisabled?: boolean;

  /** Whether or not the pop up is open. Defaults to `false`. */
  isOpen?: boolean;

  /**
   * If provided, this handler will be called on press of the confirm button.
   * If no handler is provided, the confirm button is hidden.
   */
  onConfirm?: () => void;

  /**
   * If provided, this handler will be called on press of the dismiss button.
   * If no handler is provided, the dismiss button is hidden.
   */
  onDismiss?: () => void;

  /**
   * If provided, this handler will be called on pointer downs outside the
   * modal.
   */
  onOutsidePress?: (() => void) | null;
}
