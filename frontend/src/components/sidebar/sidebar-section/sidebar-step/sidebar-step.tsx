//import { useState } from "react"
import { styled } from "styled-components";

import { SidebarStepProps } from "./sidebar-step.props";
import { color } from "../../../../theme"
import { TrashButton } from "../../../button";
import { DefaultColoredIcon } from "../../../icon/icon"
import { ContentText } from "../../../text";

const StepContainer = styled.div<{ isSelected:boolean, isCollapsed:boolean }>`
  margin: 0 5px;  
  gap:10px;
  padding: 5px;
  background-color:${({isSelected}) => isSelected ? color("protzillaLightGray"):""};
  display: flex;
  justify-content: ${({ isCollapsed }) => (isCollapsed ? "center" : "left")};
  align-items: center;
  border-radius: 6px;
`;

export const SidebarStep: React.FC<SidebarStepProps> = ({
    text,
    isCollapsed,
    sectionName,
    index,
    selectedStep,
    setSelectedStep,
    deleteStep
}: SidebarStepProps) => {

    //const [dragging, setDragging] = useState(false)

    const handleClick = () => {
        setSelectedStep({
            section: sectionName,
            index: index
        })
    }

    const handleDragStart = () => {
        //setDragging(true)
    }

    const handleDragEnd = () => {
        //setDragging(false)
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
            draggable
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            onClick={handleClick}
            isSelected={isSelected}
            isCollapsed={isCollapsed}
        >
            <DefaultColoredIcon icon="complete"/>
            <ContentText
                text={text}
                style={{"userSelect":"none"}}
            />
            {!isCollapsed && (<TrashButton onClick={handleDelete} isSmall={true} isShy={true} icon={"trash"} style={{marginLeft: "auto"}}/>)}
        </StepContainer>
        )
};
