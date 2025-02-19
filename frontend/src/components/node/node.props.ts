import { IconType } from "../icon";
import { I18nTitleProps } from "../types";

export interface Socket extends I18nTitleProps {
  id: string;
}

export interface NodeProps
  extends Omit<React.HTMLAttributes<HTMLElement>, "title">,
    I18nTitleProps {
  icon?: IconType;

  inputSockets: Socket[];
  outputSockets: Socket[];
}
