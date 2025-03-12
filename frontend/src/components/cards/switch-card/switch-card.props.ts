import type { ReactNode } from "react";

export interface SwitchCardProps {
  nameComponent1: string;
  component1: ReactNode;
  nameComponent2: string;
  component2: ReactNode;
  alignStart?: boolean;
}
