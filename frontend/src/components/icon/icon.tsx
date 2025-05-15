import React, { useState } from "react";
import { css, styled } from "styled-components";

import {
  DefaultColoredIconProps,
  DefaultColoredIconType,
  IconButtonProps,
  IconProps,
} from "./icon.props";
import * as icons from "./icons";
import { Color, color, opacity, size, Theme } from "@protzilla/theme";

/** Icon color mixin. */
// eslint-disable-next-line react-refresh/only-export-components
export const iconColor =
  <CK extends Color>(colorKey?: CK) =>
  (props: { theme: Theme }) => css`
    fill: none;
    ${props.theme.iconColorAttribute}: ${color(colorKey ?? "primary")};

    .stroke {
      stroke: ${color(colorKey ?? "primary")};
      fill: none;
    }

    .fill {
      fill: ${color(colorKey ?? "primary")};
      stroke: none;
    }
  `;

const StyledSVG = styled.svg.withConfig({
  shouldForwardProp: (prop) =>
    prop.toString() !== "isDisabled" &&
    prop.toString() !== "color" &&
    prop.toString() !== "isSmall",
})<Pick<IconProps, "color" | "isDisabled" | "isSmall" | "isBig">>`
  width: ${({ isSmall, isBig }) => size(isSmall ? "smallIcon" : isBig ? "bigIcon" : "icon")};
  height: ${({ isSmall, isBig }) => size(isSmall ? "smallIcon" : isBig ? "bigIcon" : "icon")};

  ${(props) =>
    props.isDisabled &&
    css`
      opacity: ${opacity("disabled")};
    `}

  ${(
    { color: colorKey }, // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ) => iconColor(colorKey as any)}
`;

export const Icon = React.forwardRef<SVGSVGElement, IconProps>(function Icon(
  { children, icon, ...rest },
  ref,
) {
  return (
    // TODO: Fix Vite ref passing
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, import/namespace
    <StyledSVG as={icons[icon] as any} {...rest} ref={ref}>
      {children}
    </StyledSVG>
  );
});

export const DefaultColoredIcon: React.FC<DefaultColoredIconProps> = ({ icon, style }) => {
  const defaultColors: Record<DefaultColoredIconType, Color> = {
    complete: "green",
    incomplete: "blue",
    outdated: "yellow",
    failed: "red",
  };
  return <Icon icon={icon} color={defaultColors[icon]} style={style} />;
};

export const IconButton = React.forwardRef<SVGSVGElement, IconButtonProps>(function IconButton(
  { icon, color = "primary", hoverColor = "primaryHover", ...rest },
  ref,
) {
  const [isHovered, setIsHovered] = useState(false);
  const { onMouseEnter, onMouseLeave } = rest;

  return (
    <Icon
      icon={icon}
      color={isHovered ? hoverColor : color}
      {...rest}
      onMouseEnter={(e) => {
        setIsHovered(true);
        if (onMouseEnter) onMouseEnter(e);
      }}
      onMouseLeave={(e) => {
        setIsHovered(false);
        if (onMouseLeave) onMouseLeave(e);
      }}
      ref={ref}
    />
  );
});
