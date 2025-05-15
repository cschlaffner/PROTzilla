import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import { SidebarStepProps } from "./sidebar-step.props";
import { color } from "@protzilla/theme";
import { InvisibleButton } from "../../../button";
import { DefaultColoredIconType } from "../../../icon";
import { DefaultColoredIcon } from "../../../icon/icon";
import { useNotification } from "../../../notification-center";
import { CollapsibleLabel, ContentText } from "../../../text";
import { useIconContext } from "../../use-step-icon-context.tsx";

const StepContainer = styled(motion.div)<{ isSelected: boolean }>`
  margin: 0 5px;
  gap: 10px;
  padding: 10px 5px;
  background-color: ${({ isSelected }) => (isSelected ? color("protzillaLightGray") : "")};
  display: flex;
  align-items: center;
  border-radius: 6px;
  position: relative;
`;

const TextContainer = styled.div`
  display: flex;
  gap: 5px;
  marginleft: "auto";
  max-width: 225px;
  whitespace: normal;
  line-height: 150%;

  max-height: 4.5em;
`;

export const SidebarStep: React.FC<SidebarStepProps> = ({
  number,
  name,
  stepStatus,
  isCollapsed,
  sectionName,
  sectionLength,
  index,
  isSelected,
  handleStepSelection,
  deleteStep,
  setHandlePosition,
  setShowHandle,
  setHoveredStepIndex,
}: SidebarStepProps) => {
  const notify = useNotification();

  const [isHovered, setIsHovered] = useState<boolean>(false);
  const [whiteSpace, setWhiteSpace] = useState("normal");
  const stepRef = useRef<HTMLDivElement | null>(null);

  const { icons } = useIconContext();
  const stepID = `${sectionName}-${index.toString()}`;
  const icon = icons[stepID] || stepStatus;

  useEffect(() => {
    if (isCollapsed) {
      setWhiteSpace("nowrap");
    } else {
      setTimeout(() => {
        setWhiteSpace("normal");
      }, 300);
    }
  }, [isCollapsed]);

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!stepRef.current?.parentElement?.parentElement) return;

    const rect = stepRef.current.getBoundingClientRect();
    const parentRect = stepRef.current.parentElement.parentElement.getBoundingClientRect();
    const xMidpoint = rect.left + rect.width / 2 - parentRect.left;
    const yMidpoint = rect.top + rect.height / 2;

    if (event.clientY < yMidpoint || index === sectionLength - 1) {
      setHandlePosition({ left: xMidpoint, top: rect.top - parentRect.top });
      setHoveredStepIndex(index - 1);
    } else {
      setHandlePosition({ left: xMidpoint, top: rect.bottom - parentRect.top });
      setHoveredStepIndex(index);
    }
  };

  const handleMouseLeave = (event: React.MouseEvent) => {
    //check if mouse is over add step handle
    setIsHovered(false);
    const relatedTarget = event.relatedTarget;
    if (
      !(relatedTarget instanceof HTMLElement) ||
      !relatedTarget.closest('[data-group-id="step-group"]')
    ) {
      setShowHandle(false);
    }
  };

  const handleClick = () => {
    handleStepSelection({
      section: sectionName,
      index: index,
    });
  };

  const handleDelete = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (isSelected) {
      notify({
        title: "Unallowed action",
        message: "You cannot delete the step you're currently on.",
        type: "error",
      });
      return;
    }
    deleteStep(index);
  };

  return (
    <StepContainer
      onClick={handleClick}
      isSelected={isSelected}
      onMouseEnter={() => {
        setIsHovered(true);
        setShowHandle(true);
      }}
      onMouseLeave={handleMouseLeave}
      onMouseMove={handleMouseMove}
      ref={stepRef}
    >
      <DefaultColoredIcon icon={icon as DefaultColoredIconType} style={{ flexShrink: 0 }} />
      <TextContainer>
        <ContentText text={number} style={{ userSelect: "none", whiteSpace: "nowrap" }} />
        <CollapsibleLabel width={200} isCollapsed={isCollapsed}>
          <ContentText text={name} style={{ userSelect: "none", whiteSpace: whiteSpace }} />
        </CollapsibleLabel>
      </TextContainer>
      {!isCollapsed && isHovered && (
        <InvisibleButton
          onClick={handleDelete}
          color={"gray50"}
          isSmall={true}
          isShy={true}
          icon={"trash"}
          style={{
            position: "absolute",
            left: "100%",
            transform: "translateX(-130%)",
          }}
        />
      )}
    </StepContainer>
  );
};
