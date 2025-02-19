import { I18nProps, UIStateProps } from "../types";

export type TextProps = React.HTMLAttributes<HTMLSpanElement> &
  I18nProps &
  UIStateProps;

export type LinkProps = React.AnchorHTMLAttributes<HTMLAnchorElement> &
  I18nProps &
  UIStateProps;
