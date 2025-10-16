/* eslint-disable @typescript-eslint/no-unnecessary-condition */

const platform =
  typeof window === "undefined"
    ? "node"
    : ((window?.navigator as { userAgentData?: { platform: string } })?.userAgentData?.platform ??
      // eslint-disable-next-line @typescript-eslint/no-deprecated
      window?.navigator?.platform ??
      "unknown");

export const isFirefox = (): boolean =>
  navigator ? Boolean(~navigator.userAgent.toLowerCase().indexOf("firefox")) : false;

export const isSafari = (): boolean =>
  navigator ? /^((?!chrome|android).)*safari/i.test(navigator.userAgent.toLowerCase()) : false;

export const isWindows = (): boolean =>
  platform ? Boolean(~platform.toLowerCase().indexOf("win")) : false;

export const isMac = (): boolean =>
  platform ? Boolean(~platform.toLowerCase().indexOf("mac")) : false;

export const isNode = (): boolean => platform === "node";
