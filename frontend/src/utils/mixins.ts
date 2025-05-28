import { css } from "styled-components";

/**
 * A mixin that absolutely positions an element to cover the whole area of its
 * next relatively positioned parent.
 */
export const coverMixin = css`
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
`;
