import React from "react";
import styled from "styled-components";

import { shadow } from "../../theme";
import { Tooltip, TooltipProps } from "../tooltip";

const TooltipWrapper = styled.div`
  position: relative;
  display: inline-block;
`;

const Arrow = styled.div<{ position: string }>`
  content: "";
  position: absolute;
  width: 0;
  height: 0;
  border-style: solid;
  z-index: -1;
  filter: ${shadow("tooltip")};

  ${({ position }) => position === "top" && `
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    border-width: 6px 6px 0 6px;
    border-color: grey transparent transparent transparent;
  `}

  ${({ position }) => position === "bottom" && `
    top: -6px;
    left: 50%;
    transform: translateX(-50%);
    border-width: 0 6px 6px 6px;
    border-color: transparent transparent grey transparent;
  `}

  ${({ position }) => position === "left" && `
    right: -6px;
    top: 50%;
    transform: translateY(-50%);
    border-width: 6px 0 6px 6px;
    border-color: transparent transparent transparent grey;
  `}

  ${({ position }) => position === "right" && `
    left: -6px;
    top: 50%;
    transform: translateY(-50%);
    border-width: 6px 6px 6px 0;
    border-color: transparent grey transparent transparent;
  `}
`;

export const TooltipWithArrow: React.FC<TooltipProps> = (props) => {
  return (
    <TooltipWrapper>
      <Tooltip {...props} />
      <Arrow position={props.position ?? "top"} />
    </TooltipWrapper>
  );
};

export default TooltipWithArrow;