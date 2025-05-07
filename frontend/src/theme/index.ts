import { useTheme as useSCTheme } from "styled-components";

import type { Theme } from "./theme";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const useTheme = (): Theme => useSCTheme() as any;
export { ThemeProvider } from "styled-components";

export * from "./global-styles";
export * from "./theme";
export * from "./utils";
export * from "./styled";
