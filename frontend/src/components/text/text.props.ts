import { UIStateProps } from "@protzilla/utils";

export type TextProps = React.HTMLAttributes<HTMLSpanElement> &
  UIStateProps & {
    text?: string;
  };

export type LinkProps = React.AnchorHTMLAttributes<HTMLAnchorElement> & UIStateProps;

export interface CollapsibleLabelProps {
  width: number | string;
  collapsedWidth?: number;
  isCollapsed: boolean;
  children?: React.ReactNode;
}
