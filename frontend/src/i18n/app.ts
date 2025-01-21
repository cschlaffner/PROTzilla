import baseDe from "./translations/de/base.json";
import commonDe from "./translations/de/common.json";
import baseEn from "./translations/en/base.json";
import commonEn from "./translations/en/common.json";
import { initI18nWeb } from "./web";

export const initI18nApp = async () =>
  import.meta.env.PROD
    ? initI18nWeb()
    : initI18nWeb({
        resources: {
          de: { base: baseDe, common: commonDe },
          en: { base: baseEn, common: commonEn },
        },
      });
