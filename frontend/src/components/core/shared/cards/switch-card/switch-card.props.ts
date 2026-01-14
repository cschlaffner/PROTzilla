import { SwitchComponent } from "@protzilla/utils";

export interface SwitchCardProps {
  components: SwitchComponent[];
  hasSwitchAlignStart?: boolean;
  hasCardTitle?: boolean;
  hasShadow?: boolean;
  styleProps?: React.CSSProperties;
  selection?: object;
  callback?: (arg: object) => void;
}
