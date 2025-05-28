import { useRef, useState } from "react";
import { styled, useTheme } from "styled-components";

import { Icon } from "../icon";
import { Tooltip } from "../tooltip";
import { InfoIProps } from "./info-i.props";

const Wrapper = styled.div`
  position: relative;
  display: inline-block;
  align-self: center;
`;

export const InfoIComponent: React.FC<InfoIProps> = ({ text, isSmall }) => {
  const [isShown, setIsShown] = useState<boolean>(false);
  const iconRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();
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
        <Icon icon="info" color="primary" isSmall={isSmall} />
      </div>

      {isShown && (
        <Tooltip
          text={text}
          isShown={true}
          distance={parseInt(theme.spacing.small)}
          anchor={iconRef.current ?? undefined}
          position="top"
        />
      )}
    </Wrapper>
  );
};

export default InfoIComponent;
