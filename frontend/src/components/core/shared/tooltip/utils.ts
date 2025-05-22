/* eslint-disable @typescript-eslint/prefer-nullish-coalescing */
import {
  Pixel,
  RelativePositionConfig,
  RelativePositionStyleConfig,
  useDelay,
  useModalRoot,
  useRelativePosition,
} from "@protzilla/hooks";
import { duration, useTheme } from "@protzilla/theme";
import React, { useCallback, useEffect, useState } from "react";

export type TooltipPosition = "left" | "right" | "bottom" | "bottomLeft" | "bottomRight" | "top";
export type TooltipPositionConfig = RelativePositionConfig<TooltipPosition>;

const defaultTooltipDistance = 0;

/**
 * Returns a style object that absolutely positions a tooltip next to the
 * element it refers to.
 */
const computeStyle = ({
  position = "bottom",
  distance = defaultTooltipDistance,
  rect,
  offsetRect,
}: RelativePositionStyleConfig<TooltipPosition>): React.CSSProperties => {
  switch (position) {
    case "left":
      return {
        position: "absolute",
        top: rect.top + rect.height / 2 - (offsetRect?.top || 0),
        right:
          (offsetRect?.right || document.body.getBoundingClientRect().width) -
          (rect.left - distance),
        transform: "translateY(-50%)",
      };

    case "bottom":
      return {
        position: "absolute",
        top: rect.bottom + distance - (offsetRect?.top || 0),
        left: rect.left + rect.width / 2 - (offsetRect?.left || 0),
        transform: "translateX(-50%)",
      };

    case "bottomRight":
      return {
        position: "absolute",
        top: rect.bottom + distance - (offsetRect?.top || 0),
        left: rect.right + distance - (offsetRect?.left || 0),
      };

    case "top":
      return {
        position: "absolute",
        top: rect.top + distance - (offsetRect?.bottom || 50),
        left: rect.left + rect.width / 2 - (offsetRect?.left || 0),
        transform: "translateX(-50%)",
      };

    default:
      return {
        position: "absolute",
        top: rect.top + rect.height / 2 - (offsetRect?.top || 0),
        left: rect.right + distance - (offsetRect?.left || 0),
        transform: "translateY(-50%)",
      };
  }
};

/**
 * Returns properties for the tooltip and event handlers for the parent.
 */
export const useTooltipPosition = (config: TooltipPositionConfig): React.CSSProperties =>
  useRelativePosition(computeStyle, config);

export const useTooltipScheduling: (
  useMouseAnchor?: boolean,
  showImmediately?: boolean,
) => {
  handlePointerEnter: () => void;
  handlePointerLeave: () => void;
  showTooltip: boolean;
  mouseAnchor: Pixel | null;
} = (useMouseAnchor = true, showImmediately = false) => {
  const theme = useTheme();

  const modalRoot = useModalRoot().current;
  const modalRootRect = modalRoot?.getBoundingClientRect();

  const [mouseAnchor, setMouseAnchor] = useState(
    modalRootRect ? { x: modalRootRect.left, y: modalRootRect.top } : { x: 0, y: 0 },
  );

  const updateMouseAnchor = useCallback(
    (event: PointerEvent | React.PointerEvent) => {
      setMouseAnchor(
        modalRootRect
          ? {
              x: event.clientX - modalRootRect.left,
              y: event.clientY - modalRootRect.top,
            }
          : { x: event.clientX, y: event.clientY },
      );
    },
    [modalRootRect],
  );

  const [showTooltip, setShowTooltip] = useState(false);
  const [scheduleTooltip, cancelTooltip] = useDelay(
    useCallback(() => {
      setShowTooltip(true);
    }, []),
    duration("tooltipDelay")({ theme }) as number,
  );

  const [scheduleTooltipsDelay, cancelTooltipsDelay] = useDelay(
    useCallback(() => {
      theme.setShouldForceTooltip(false);
    }, [theme]),
    duration("noTooltipDelayInterval")({ theme }) as number,
  );
  const setNoTooltipDelayTimer = useCallback(() => {
    theme.setShouldForceTooltip(true);
    scheduleTooltipsDelay();
  }, [scheduleTooltipsDelay, theme]);

  const [isHovered, setIsHovered] = useState(false);
  const onPointerEnter = useCallback(() => {
    setIsHovered(true);
    cancelTooltipsDelay();
    scheduleTooltip();
  }, [cancelTooltipsDelay, scheduleTooltip]);

  const onPointerLeave = useCallback(() => {
    setIsHovered(false);
    if (showTooltip || theme.shouldForceTooltip) setNoTooltipDelayTimer();
    cancelTooltip();
    setShowTooltip(false);
  }, [showTooltip, theme.shouldForceTooltip, setNoTooltipDelayTimer, cancelTooltip]);

  useEffect(() => {
    if (isHovered && useMouseAnchor) {
      document.addEventListener("pointermove", updateMouseAnchor);

      return () => {
        document.removeEventListener("pointermove", updateMouseAnchor);
      };
    }

    return () => {
      // Intentionally left blank
    };
  }, [isHovered, updateMouseAnchor, useMouseAnchor]);

  return {
    handlePointerEnter: onPointerEnter,
    handlePointerLeave: onPointerLeave,
    showTooltip:
      showTooltip || (theme.shouldForceTooltip && isHovered) || (showImmediately && isHovered),
    mouseAnchor: useMouseAnchor ? mouseAnchor : null,
  };
};
