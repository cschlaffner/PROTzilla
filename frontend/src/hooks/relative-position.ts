import { useLayoutEffect, useRef, useState } from "react";

import { useUpdateOnResize } from "./update-on-resize";

export interface Pixel {
  x: number;
  y: number;
}

export interface RelativePositionConfig<P = void> {
  /** The anchor element or position. */
  anchor?: HTMLElement | SVGSVGElement | Pixel | null;

  /**
   * If set to `true`, the position is actively updated.
   * Defaults to `true`.
   */
  isActive?: boolean;

  /**
   * If set to `true`, the position will be returned relative to its offset
   * parent.
   */
  positionRelativeToOffsetParent?: boolean;

  /** The position relative to its parent. */
  position?: P;

  /**
   * The positioned element's distance to its parent.
   * Defaults to a value based on the current theme.
   */
  distance?: number;

  /** Style overrides. */
  style?: React.CSSProperties;
}

export interface RelativePositionStyleConfig<P = void> extends Pick<
  RelativePositionConfig<P>,
  "distance" | "position"
> {
  /** The parent element's bounding client rect. */
  rect: DOMRect;

  /** The offset parent's bounding client rect (if any). */
  offsetRect?: DOMRect;
}

/**
 * Returns a style object that absolutely positions an element next to the
 * parent element it refers to.
 */
export const useRelativePosition = <P = void>(
  computeStyle: (config: RelativePositionStyleConfig<P>) => React.CSSProperties,
  {
    anchor,
    isActive = true,
    positionRelativeToOffsetParent,
    position,
    distance,
    style: styleOverride,
  }: RelativePositionConfig<P>,
): React.CSSProperties => {
  useUpdateOnResize(isActive);

  const [style, setStyle] = useState<React.CSSProperties>({});
  const rectRef = useRef<Partial<DOMRect>>({});
  const offsetRectRef = useRef<Partial<DOMRect> | undefined>();
  const configRef = useRef<Partial<RelativePositionConfig<P>> | undefined>();

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useLayoutEffect(() => {
    if (!isActive) return;

    const rect: DOMRect | undefined =
      !anchor || (anchor as Element).nodeName
        ? // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
          (anchor as Element)?.getBoundingClientRect()
        : new DOMRect((anchor as Pixel).x, (anchor as Pixel).y);
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    if (!rect) return;

    const offsetRect = positionRelativeToOffsetParent
      ? (anchor as HTMLElement).offsetParent?.getBoundingClientRect()
      : undefined;

    // Prevent unnecessary updates
    if (
      rectRef.current.top === rect.top &&
      rectRef.current.left === rect.left &&
      rectRef.current.bottom === rect.bottom &&
      rectRef.current.right === rect.right &&
      offsetRectRef.current?.top === offsetRect?.top &&
      offsetRectRef.current?.left === offsetRect?.left &&
      offsetRectRef.current?.bottom === offsetRect?.bottom &&
      offsetRectRef.current?.right === offsetRect?.right &&
      configRef.current?.positionRelativeToOffsetParent === positionRelativeToOffsetParent &&
      configRef.current?.position === position &&
      configRef.current?.distance === distance
    ) {
      return;
    }
    rectRef.current = rect;
    offsetRectRef.current = offsetRect;
    configRef.current = { positionRelativeToOffsetParent, position, distance };

    setStyle(computeStyle({ position, distance, rect, offsetRect }));
  });

  return styleOverride ? { ...style, ...styleOverride } : style;
};
