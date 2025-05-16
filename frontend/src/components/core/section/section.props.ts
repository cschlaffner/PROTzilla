import type React from "react";

import type { SectionTitleProps } from "@protzilla/core";

export type SectionProps = Omit<React.HTMLAttributes<HTMLDivElement>, "title"> &
  Omit<SectionTitleProps, "baseElement">;
