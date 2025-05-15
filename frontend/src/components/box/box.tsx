import { color, radius, zIndex } from "@protzilla/theme";
import { styled } from "styled-components";

import { coverMixin } from "../mixins";
import { BoxProps } from "./box.props";

export const FlexColumn = styled.div<BoxProps>`
  align-items: flex-start;
  display: flex;
  flex-direction: column;
`;

export const FlexRow = styled.div<BoxProps>`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

export const Spacer = styled.div<BoxProps & { flex?: number }>`
  flex: ${(props) => (props.flex ? String(props.flex) : "1")};
`;

/** The modal root. There should only be one per application. */
export const ModalRoot = styled.div.attrs(({ theme }) => ({
  id: theme.modalRootId,
}))`
  ${coverMixin}
  pointer-events: none;
  z-index: ${zIndex("modal")};
`;

export const FocusOutline = styled.div`
  border: 1px solid ${color("primary")};
  border-radius: ${radius("buttonFocusOutline")};
  bottom: -3px;
  display: none;
  left: -3px;
  position: absolute;
  right: -3px;
  top: -3px;
`;
