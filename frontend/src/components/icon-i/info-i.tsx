import { useRef, useState } from "react";
import styled from "styled-components";

import { Icon } from "../icon";
import { InfoIProps } from "./info-i.props";
import { Tooltip } from "../tooltip";

const IconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
`;

const Wrapper = styled.div`
  position: relative; /* Das gesamte Icon bleibt positioniert */
  display: inline-block;
`;

const TooltipContainer = styled.div<{ position: string }>`
  position: absolute;

  ${({ position }) => position === "top" && `
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-bottom: 8px;
  `}

  /* Tooltip-Pfeil */
  &::before {
    content: "";
    position: absolute;
    border-style: solid;
    display: block;
    width: 0;
    height: 0;
  }

  ${({ position }) => position === "top" && `
    &::before {
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      border-width: 6px 6px 0 6px;
      border-color: white transparent transparent transparent;
    }
  `}

  ${({ position }) => position === "bottom" && `
    &::before {
      top: -6px;
      left: 50%;
      transform: translateX(-50%);
      border-width: 0 6px 6px 6px;
      border-color: transparent transparent white transparent;
    }
  `}

  ${({ position }) => position === "left" && `
    &::before {
      right: -6px;
      top: 50%;
      transform: translateY(-50%);
      border-width: 6px 0 6px 6px;
      border-color: transparent transparent transparent white;
    }
  `}

  ${({ position }) => position === "right" && `
    &::before {
      left: -6px;
      top: 50%;
      transform: translateY(-50%);
      border-width: 6px 6px 6px 0;
      border-color: transparent white transparent transparent;
    }
  `}
`;

export const InfoIComponent: React.FC<InfoIProps> = ({ text, position = "top", triggerType = "hover" }) => {
  const [isShown, setIsShown] = useState<boolean>(false);
  const iconRef = useRef<HTMLButtonElement>(null);

  return (
    <Wrapper>
      <IconButton
        ref={iconRef}
        onMouseEnter={triggerType === "hover" ? () => { setIsShown(true); } : undefined}
        onMouseLeave={triggerType === "hover" ? () => { setIsShown(false); } : undefined}
        onClick={triggerType === "click" ? () => { setIsShown((prev) => !prev); } : undefined}
      >
        <Icon icon="info" color="primary" />
      </IconButton>

      {isShown && (
        <TooltipContainer position={position}>
          <Tooltip
            text={<div>{text}</div>}
            isShown={true}
            anchor={iconRef.current ?? undefined}
            position={position} />
        </TooltipContainer>
      )}
    </Wrapper>
  );
};

export default InfoIComponent;