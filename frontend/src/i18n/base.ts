import i18n, { InitOptions, Module, Newable, TFunction } from "i18next";
import moment from "moment";
import { initReactI18next } from "react-i18next";

import { isAmount } from "../utils";

export const formatDates = (
  value: Date,
  _lng: string | undefined,
  options: { pattern?: string },
): string =>
  options.pattern === "QUARTER"
    ? `Q${String(moment(value).quarter())}/${moment(value).format("YY")}`
    : moment(value).format(options.pattern ?? "DD.MM.YYYY");

/** Default i18next currency formatter which defaults the currency to EUR. */
export const formatCurrency = (
  value: number,
  lng: string | undefined,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  options: any,
): string =>
  new Intl.NumberFormat(lng, {
    style: "currency",
    currency: isAmount(value) ? value.unit : "EUR",
    ...(options || {}),
  }).format(isAmount(value) ? value.value : value);

export interface I18nConfig {
  modules?: (Module | Newable<Module>)[];

  resources?: Record<string, Record<string, Record<string, string>>>;

  initOptions?: InitOptions;
}

export const initI18n = async (config?: I18nConfig): Promise<TFunction> => {
  moment.updateLocale("en", {
    calendar: {
      lastDay: "[Yesterday]",
      sameDay: "[Today]",
      nextDay: "[Tomorrow]",
      lastWeek: "dddd",
      sameElse: "L",
    },
  });
  moment.updateLocale("de", {
    calendar: {
      lastDay: "[Gestern]",
      sameDay: "[Heute]",
      nextDay: "[Morgen]",
      lastWeek: "dddd",
      sameElse: "L",
    },
  });
  i18n.on("languageChanged", (lng) => {
    moment.locale(lng.split("-")[0]);
  });

  let instance = i18n;
  config?.modules?.forEach((module) => {
    instance = instance.use(module);
  });
  const t = await instance.use(initReactI18next).init({
    supportedLngs: ["en", "de"],
    fallbackLng: "en",
    load: "languageOnly",

    ns: ["base", "common"],
    defaultNS: "common",

    interpolation: {
      // React is XSS-safe already
      escapeValue: false,
    },

    resources: config?.resources,

    compatibilityJSON: "v4",
    ...config?.initOptions,
  });

  instance.services.formatter?.add("datetime", formatDates);
  instance.services.formatter?.add("currency", formatCurrency);

  return t;
};
