import { TFunction } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";

import { I18nConfig, initI18n } from "./base";

export const initI18nWeb = async (config?: I18nConfig): Promise<TFunction> =>
  initI18n({
    modules: config?.resources ? [LanguageDetector] : [LanguageDetector, Backend],
    initOptions: {
      backend: config?.resources
        ? undefined
        : {
            loadPath: `${import.meta.env.BASE_URL || "/"}assets/{{lng}}/{{ns}}.json`,
          },
    },
    ...config,
  });
