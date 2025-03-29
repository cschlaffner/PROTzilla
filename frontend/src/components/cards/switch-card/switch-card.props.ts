import type { ReactNode } from "react";

export interface SwitchCardProps {
  nameComponent1: string;
  component1: ReactNode;
  nameComponent2: string;
  component2: ReactNode;
  hasSwitchAlginStart?: boolean;
  hasCardTitle?: boolean;
  styleProps?: React.CSSProperties;
}
