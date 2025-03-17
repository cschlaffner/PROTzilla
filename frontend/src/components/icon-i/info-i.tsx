import { useRef, useState } from "react";
import { styled } from "styled-components";

import { Icon } from "../icon";
import { Tooltip } from "../tooltip";
import { InfoIProps } from "./info-i.props";

const Wrapper = styled.div`
  position: relative; /* Das gesamte Icon bleibt positioniert */
  display: inline-block;
`;

const IconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
`;

export const InfoIComponent: React.FC<InfoIProps> = ({ text }) => {
  const [isShown, setIsShown] = useState<boolean>(false);
  const iconRef = useRef<HTMLButtonElement>(null);

  return (
    <Wrapper>
      <IconButton
        ref={iconRef}
        onMouseEnter={() => {
          setIsShown(true);
        }}
        onMouseLeave={() => {
          setIsShown(false);
        }}
      >
        <Icon icon="info" color="primary" />
      </IconButton>

      {isShown && (
        <Tooltip
          text={<div>{text}</div>}
          isShown={true}
          distance={25}
          anchor={iconRef.current ?? undefined}
          position="top"
        />
      )}
    </Wrapper>
  );
};

export default InfoIComponent;
