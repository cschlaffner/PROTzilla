import { styled } from "styled-components";

import { SidebarStepProps } from "./sidebar-step.props";
import { color } from "../../../../theme"
import { InvisibleButton } from "../../../button";
import { DefaultColoredIcon } from "../../../icon/icon"
import { ContentText } from "../../../text";
import { CollapsibleLabel } from "../../../text-field";
import { motion } from "framer-motion"
import { useState, useRef } from "react";

const StepContainer = styled(motion.div)<{isSelected:boolean}>`
  margin: 0 5px;  
  gap: 10px;
  padding: 10px 5px;
  background-color: ${({isSelected}) => isSelected ? color("protzillaLightGray") : ""};
  display: flex;
  align-items: center;
  border-radius: 6px;
  position: relative;
`;

const TextContainer = styled.div`
    display: flex;
    gap: 5px;
    marginLeft: "auto";
    max-width: 225px;
    whiteSpace: normal;
    max-height: 3em;
`;

export const SidebarStep: React.FC<SidebarStepProps> = ({
    number,
    name,
    isCollapsed,
    sectionName,
    sectionLength,
    index,
    selectedStep,
    setSelectedStep,
    deleteStep,
    setHandlePosition,
    setShowHandle,
    setHoveredStepIndex
}: SidebarStepProps) => {

    const [isHovered, setIsHovered] = useState<boolean>(false)
    const stepRef = useRef<HTMLDivElement | null>(null)

    const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {

        if (!stepRef.current || !stepRef.current.parentElement?.parentElement) return;
    
        const rect = stepRef.current.getBoundingClientRect();
        const parentRect = stepRef.current.parentElement.parentElement.getBoundingClientRect(); 
        const xMidpoint = rect.left + rect.width / 2 - parentRect.left;
        const yMidpoint = rect.top + rect.height / 2;
    
        if (event.clientY < yMidpoint || index === sectionLength-1) {
            setHandlePosition({ left: xMidpoint, top: rect.top - parentRect.top });
            setHoveredStepIndex(index-1)
        } else {
            setHandlePosition({ left: xMidpoint, top: rect.bottom  - parentRect.top });
            setHoveredStepIndex(index)
        }
    };

    const handleMouseLeave = (event: React.MouseEvent) => {
        //check if mouse is over add step handle
        setIsHovered(false)
        const relatedTarget = event.relatedTarget as HTMLElement | null;
        if (!relatedTarget?.closest(`[data-group-id="step-group"]`)) {
            setShowHandle(false)
        }
      };

      const handleClick = () => {
        setSelectedStep({
            section: sectionName,
            index: index
        })
    }

    const handleDelete = (event: React.MouseEvent) => {
        event.stopPropagation()
        deleteStep(index)
    }

    const isSelected =
        selectedStep.section === sectionName &&
        selectedStep.index === index

    return(
        <StepContainer
            onClick={handleClick}
            isSelected={isSelected}
            onMouseEnter={() => {
                setIsHovered(true)
                setShowHandle(true)
                }}
            onMouseLeave={handleMouseLeave}
            onMouseMove={handleMouseMove}
            ref={stepRef}
        >
            <DefaultColoredIcon icon="complete" style={{ flexShrink: 0 }}/>
            <TextContainer>
            <ContentText
                    text={number}
                    style={{userSelect:"none", whiteSpace: "nowrap"}}
                />
            <CollapsibleLabel width={200} isCollapsed={isCollapsed}>
                <ContentText
                    text={name}
                    style={{userSelect:"none", whiteSpace: isCollapsed ? "nowrap":"normal"}}
                />
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
                        transform: "translateX(-130%)"
                    }}
                />
            )}
                
        </StepContainer>
        )
    };
