import type { ReactNode } from "react";

export interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
}
