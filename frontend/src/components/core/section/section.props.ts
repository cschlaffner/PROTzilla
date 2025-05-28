import type { SectionTitleProps } from "@protzilla/core";
import type React from "react";

export type SectionProps = Omit<React.HTMLAttributes<HTMLDivElement>, "title"> &
  Omit<SectionTitleProps, "baseElement">;
