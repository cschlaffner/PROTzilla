import { useModalRoot } from "@protzilla/hooks";
import { color, fontSize, fontWeight, shadow, size, zIndex } from "@protzilla/theme";
import ReactDOM from "react-dom";
import { styled } from "styled-components";

import { Text } from "../text";
import { TooltipProps } from "./tooltip.props";
import { useTooltipPosition } from "./utils";

const TooltipContainer = styled.div<Pick<TooltipProps, "baseZIndex">>`
  align-items: center;
  background: ${color("background")};
  border: 1px solid ${color("divider")};
  border-radius: 10px;
  box-shadow: ${shadow("tooltip")};
  box-sizing: border-box;
  display: flex;
  padding: 0 14px;
  z-index: ${(props) => (props.baseZIndex ?? (zIndex("tooltip")(props) as number)) + 1};
`;

const TooltipLabel = styled(Text)`
  color: ${color("primary")};
  font-weight: ${fontWeight("bold")};
  font-size: ${fontSize("small")};
  user-select: none;
  white-space: normal;
  max-width: ${size("tooltipMaxWidth")};
`;

export const Tooltip: React.FC<TooltipProps> = ({
  text,
  isShown,
  anchor,
  position,
  distance,
  style,
  ...rest
}) => {
  const modalRootRef = useModalRoot();

  const tooltipStyle = useTooltipPosition({
    anchor,
    isActive: isShown,
    positionRelativeToOffsetParent: false,
    position,
    distance,
    style,
  });

  const node =
    isShown === false ? null : (
      <TooltipContainer {...rest} style={tooltipStyle}>
        <TooltipLabel text={text} />
      </TooltipContainer>
    );

  return modalRootRef.current ? ReactDOM.createPortal(node, document.body) : node;
};
