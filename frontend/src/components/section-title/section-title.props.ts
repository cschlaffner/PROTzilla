import type { I18nDescriptionProps, I18nTitleProps } from "../types";
import type { baseComponents } from "./base-components";

export interface SectionTitleProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, "title">,
    I18nTitleProps,
    I18nDescriptionProps {
  baseComponent?: keyof typeof baseComponents;
}
