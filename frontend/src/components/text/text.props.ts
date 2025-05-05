import { I18nProps, UIStateProps } from "../types";

export type TextProps = React.HTMLAttributes<HTMLSpanElement> &
  I18nProps &
  UIStateProps;

export type LinkProps = React.AnchorHTMLAttributes<HTMLAnchorElement> &
  I18nProps &
  UIStateProps;

  export interface CollapsibleLabelProps {
    width: number | string;
    collapsedWidth?: number;
    isCollapsed: boolean;
    children?: React.ReactNode;
  }
  