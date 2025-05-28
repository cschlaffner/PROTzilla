import type React from "react";

export type BoxProps = React.HTMLAttributes<HTMLDivElement>;

export interface MainContentProps extends React.HTMLProps<HTMLDivElement> {
  /**
   * If set to true, lifts the maximum width constrain of the content
   * container.
   */
  useFullWidth?: boolean;
}
