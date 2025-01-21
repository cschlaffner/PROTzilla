import React from "react";
import { css, styled } from "styled-components";

import { IconProps } from "./icon.props";
import * as icons from "./icons";
import { color, opacity, size, Theme } from "../../theme";

/** Icon color mixin. */
// eslint-disable-next-line react-refresh/only-export-components
export const iconColor =
  <CK extends keyof Theme["colors"]>(colorKey?: CK) =>
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
})<Pick<IconProps, "color" | "isDisabled" | "isSmall">>`
  width: ${({ isSmall }) => size(isSmall ? "smallIcon" : "icon")};
  height: ${({ isSmall }) => size(isSmall ? "smallIcon" : "icon")};

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
