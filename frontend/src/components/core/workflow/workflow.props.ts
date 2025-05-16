import type React from "react";

import type { IconType } from "@protzilla/core";

export interface WorkflowProps {
  icon?: IconType;
  workflow?: string;
  onPress?: (
    event: React.PointerEvent<HTMLButtonElement> | React.KeyboardEvent<HTMLButtonElement>,
  ) => void;
}
