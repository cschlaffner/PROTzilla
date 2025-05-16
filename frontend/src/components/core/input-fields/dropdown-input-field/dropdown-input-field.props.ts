import type { UIStateProps } from "@protzilla/utils";

import { InputContainerProps } from "@protzilla/core";

export interface DropdownInputFieldProps extends InputContainerProps, UIStateProps {
  options: { label: string; value: string }[];
  value?: string | null;
  onChange: (value: string | null) => void;
}
