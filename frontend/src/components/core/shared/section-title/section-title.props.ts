import type { baseComponents } from "./base-components";

export interface SectionTitleProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  title?: string;
  description?: string;
  baseComponent?: keyof typeof baseComponents;
}
