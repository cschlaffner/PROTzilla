import type { ReactNode } from "react";

export interface CardProps {
  title?: string | ReactNode;
  children: ReactNode;
  className?: string;
}
