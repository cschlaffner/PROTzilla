import { useRef, useState } from "react";
import { styled } from "styled-components";

import { Icon } from "../icon";
import { Tooltip } from "../tooltip";
import { InfoIProps } from "./info-i.props";

const Wrapper = styled.div`
  position: relative; /* Das gesamte Icon bleibt positioniert */
  display: inline-block;
`;

export const InfoIComponent: React.FC<InfoIProps> = ({ text }) => {
  const [isShown, setIsShown] = useState<boolean>(false);
  const iconRef = useRef<HTMLDivElement>(null);

  return (
    <Wrapper>
      <div
        ref={iconRef}
        onMouseEnter={() => {
          setIsShown(true);
        }}
        onMouseLeave={() => {
          setIsShown(false);
        }}
      >
        <Icon icon="info" color="primary" />
      </div>

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
