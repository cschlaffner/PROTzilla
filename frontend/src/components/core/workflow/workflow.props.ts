import type { IconType } from "@protzilla/core/shared";
import type React from "react";

export interface WorkflowProps {
  icon?: IconType;
  workflow?: string;
  onPress?: (
    event: React.PointerEvent<HTMLButtonElement> | React.KeyboardEvent<HTMLButtonElement>,
  ) => void;
}
