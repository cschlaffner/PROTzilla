import { action, makeObservable, observable } from "mobx";

export const defaultPalette = {
  mode: "light",

  background: "#FFF",
  backgroundOffset: "#F8F8F8",

  text: "#2C2E34",
  textDisabled: "#C0C0C2",
  onPrimary: "#FFF",

  protzillaGray: "#E0E0E0",
  protzillaLightGray: "#E8EDF3",
  protzillaDarkBlue: "#4A536A",  
  protzillaLightBlue: "#F7F6FE",
  protzillaRed: "#CE5A5A",

  primary: "#4A536A",
  primaryHover: "#CE5A5A",
  primaryActive: "#4A536A",
  primaryDisabled: "#C0C0C2",

  secondary: "#E8EDF3",
  secondaryHover: "#000000",
  secondaryActive: "#E8EDF3",
  secondaryDisabled: "#F2F2F3",

  link: "#2C2E34",
  linkDisabled: "#E4E4E4",

  divider: "#EAEAEB",

  red: "#CE5A5A",
  redHover: "#CE5A5A",
  redActive: "#CE5A5A",
  redDisabled: "#CE5A5A",

  gray: "#E0E0E0",  
  grayHover: "#FFFFFF",
  grayActive: "#E0E0E0",
  grayDisabled: "#E0E0E0",

  yellow: "#ED9804",
  yellowHover: "#ED9804",
  yellowActive: "#ED9804",
  yellowDisabled: "#FDF5E6",

  green: "#18723F",
  greenHover: "#18723F",
  greenActive: "#18723F",
  greenDisabled: "#E8f1EC",

  blue: "#004CA2",
  blueHover: "#004CA2",
  blueActive: "#004CA2",
  blueDisabled: "#E5EDF6",

  black: "#000000",
  blackDisabled: "#F2F2F3",
  
  lightGray12: "#44464b",
  gray6: "#E4E4E5",
  gray50: "#929396",

  invisibleHover: "#CE5A5A",
  transparent: "rgba(0,0,0,0)",
  popUpBackdrop: "rgba(44,46,52,0.20)",
};

const colorModes = {
  light: defaultPalette,
  dark: defaultPalette,
};

export const baseTheme = {
  /**
   * The id of the applications root element for absolutely positioned overlays
   * such as modals or tooltips.
   *
   * This should not change while the application is running.
   * Unset it here if you are not using a dedicated modal root.
   */
  modalRootId: "modal-root",

  /**
   * The default CSS attribute used for coloring icons.
   * This is typically either `"stroke"` or `"fill"`.
   */
  iconColorAttribute: "stroke",

  borders: {},
  borderWidths: {},
  breakpoints: {
    /** Phone. */
    xs: 0,
    /** Tablet portrait. */
    sm: 600,
    /** Tablet landscape. */
    md: 900,
    /** Desktop. */
    lg: 1200,
    /** Big desktop. */
    xl: 1536,
  },
  colors: defaultPalette,
  direction: "ltr",
  durations: {
    shortest: 150,
    shorter: 200,
    short: 250,
    default: 300,
    complex: 375,
    enteringScreen: 225,
    leavingScreen: 195,

    tooltipDelay: 400,
    noTooltipDelayInterval: 1000,
    successDisplayDuration: 5000,
    successButtonDuration: 2000,
    errorDisplayDuration: 10000,
  },
  fonts: {
    default: "Helvetica Neue",
    defaultWithFallbacks: "Helvetica Neue, Helvetica, Arial, sans-serif",
  },
  fontSizes: {
    h1: "40px",
    h1Mobile: "26px",
    h2: "26px",
    h2Mobile: "22px",
    h3: "20px",
    h4: "18px",
    h5: "16px",
    h6: "14px",
    button: "14px",
    default: "12px",
    small: "10px",
    tagSmall: "8px",
  },
  fontWeights: {
    bold: "700",
    regular: "400",
    light: "300",
    default: "400",
    medium: "500",
  },
  letterSpacings: {},
  lineHeights: {},
  mediaQueries: {
    print: "@media print",
  },
  opacities: {
    disabled: 0.25,
  },
  radii: {
    default: "8px",
    button: "6px",
    smallButton: "4px",
    buttonFocusOutline: "8px",
    smallCard: "12px",
    card: "20px",
  },
  shadows: {
    floating: "0px 12px 20px -10px rgba(0, 0, 0, 0.25)",
    tooltip: "0px 3px 8px -4px rgba(0, 0, 0, 0.3)",
  },
  sizes: {
    icon: "20px",
    smallIcon: "12px",
    swatch: "16px",
    buttonHeight: "40px",
    smallButtonHeight: "24px",
    smallDropdownHeight: "32px",
    largeAvatar: "100px",
    navigationItemWidth: "240px",
  },
  spacing: {
    listIndentation: "14px",
    buttonPadding: "12px 14px",
    buttonIconPadding: "10px",
    smallButtonPadding: "6px 10px",
    smallButtonIconPadding: "8px",
    buttonGap: "8px",
    smallButtonGap: "6px",

    small: "10px",
    medium: "20px",
    large: "50px",
  },
  zIndices: {
    drawer: 1200,
    modal: 1300,
    notification: 1400,
    tooltip: 1500,

    background: 0,
    tick: 1,
    baseElement: 2,
    label: 3,
    indicator: 4,
  },
};

export type ColorMode = keyof typeof colorModes;

export type BreakpointQueries<T> = {
  [K in keyof T as K extends string
    ? `${K}-up` | `${K}-down` | `${K}-only`
    : never]: string;
};

export const getMediaQueriesFromBreakpoints = <
  T extends Record<string, number>,
>(
  breakpoints: T,
): BreakpointQueries<T> => {
  const result: Record<string, string> = {};

  const keys = Object.keys(breakpoints) as (keyof typeof breakpoints &
    string)[];
  keys.forEach((key, index) => {
    result[`${key}-up`] = `@media (min-width: ${String(breakpoints[key])}px)`;
    result[`${key}-down`] = `@media (max-width: ${String(breakpoints[key])}px)`;

    result[`${key}-only`] =
      index === 0
        ? // First breakpoint
          `@media (max-width: ${String(
            Math.max(0, breakpoints[keys[index + 1]] - 1),
          )}px)`
        : index === keys.length - 1
          ? // Last breakpoint
            `@media (min-width: ${String(breakpoints[keys[index - 1]] + 1)}px)`
          : // Middle breakpoint
            `@media (min-width: ${String(
              breakpoints[keys[index - 1]] + 1,
            )}px) and (max-width: ${String(
              Math.max(0, breakpoints[keys[index + 1]] - 1),
            )}px)`;
  });

  return result as BreakpointQueries<T>;
};

/**
 * Returns a theme for the given color mode.
 *
 * @param colorMode The color mode, defaults to `light`.
 * @param theme If given, overrides the default theme template.
 */
export const getTheme = (
  colorMode: ColorMode = "light",
  theme: typeof baseTheme = baseTheme,
) =>
  makeObservable(
    {
      ...theme,
      // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
      colors: colorModes[colorMode] || theme.colors,
      mediaQueries: {
        ...theme.mediaQueries,
        ...getMediaQueriesFromBreakpoints(theme.breakpoints),
      },

      /**
       * Indicates whether tooltips should be shown immediately on hover,
       * without the default delay.
       */
      shouldForceTooltip: false,

      /**
       * Sets whether tooltips should be shown immediately on hover,
       * without the default delay.
       */
      setShouldForceTooltip(shouldForceTooltip: boolean) {
        this.shouldForceTooltip = shouldForceTooltip;
      },
    },
    {
      colors: observable,
      shouldForceTooltip: observable,

      setShouldForceTooltip: action,
    },
  );

export type Theme = ReturnType<typeof getTheme>;
