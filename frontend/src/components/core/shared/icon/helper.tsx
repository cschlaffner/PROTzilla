import { Color, color, Theme } from "@protzilla/theme";
import { css } from "styled-components";

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