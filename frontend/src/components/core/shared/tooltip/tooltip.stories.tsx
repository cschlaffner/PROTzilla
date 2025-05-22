import { color } from "@protzilla/theme";
import React, { useState } from "react";
import { styled } from "styled-components";

import { Tooltip } from "./tooltip";
import { TooltipProps } from "./tooltip.props";
import { useTooltipScheduling } from "./utils";

export default {
  component: Tooltip,
  title: "Tooltip",
};

export const primary = (args: TooltipProps): React.ReactNode => <Tooltip {...args} />;
primary.args = {
  isShown: true,
  text: "This is a tooltip",
  tx: "",
  position: "bottom",
  anchor: { x: 100, y: 100 },
};

const Box = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 10px;
  background-color: ${color("primary")};
`;

const BoxWithTooltipDelay = ({
  args: { useMouseAnchor, ...rest },
}: {
  args: Omit<TooltipProps, "isShown" | "anchor"> & { useMouseAnchor: boolean };
}) => {
  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(useMouseAnchor);

  const [parentRef, setParentRef] = useState<HTMLDivElement | null>(null);

  return (
    <Box ref={setParentRef} onPointerEnter={handlePointerEnter} onPointerLeave={handlePointerLeave}>
      <Tooltip {...rest} isShown={showTooltip} anchor={useMouseAnchor ? mouseAnchor : parentRef} />
    </Box>
  );
};
export const onHover = (
  args: Omit<TooltipProps, "isShown" | "anchor"> & { useMouseAnchor: boolean },
): React.ReactNode => <BoxWithTooltipDelay args={args} />;
onHover.args = {
  distance: 13,
  position: "bottomRight",
  text: "This tooltip appears after a delay",
  useMouseAnchor: true,
};
