import { TooltipWithArrow } from "./tooltip-with-arrow";
import { TooltipWithArrowProps } from "./tooltip-with-arrow.props";

export const primary = (args: TooltipWithArrowProps): React.ReactNode => (
  <TooltipWithArrow {...args} />
);
primary.args = {
  isShown: true,
  text: "This is a tooltip",
  tx: "",
  position: "bottom",
  anchor: { x: 100, y: 100 },
};