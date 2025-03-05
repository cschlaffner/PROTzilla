//import { useState } from "react"
import { styled } from "styled-components";

import { SidebarStepProps } from "./sidebar-step.props";
import { color } from "../../../../theme"
import { TrashButton } from "../../../button";
import { DefaultColoredIcon } from "../../../icon/icon"
import { ContentText } from "../../../text";
import { CollapsibleLabel } from "../../../text-field";

const StepContainer = styled.div<{ isSelected:boolean, isCollapsed:boolean }>`
  margin: 0 5px;  
  gap: 10px;
  padding: 5px;
  background-color:${({isSelected}) => isSelected ? color("protzillaLightGray"):""};
  display: flex;
  align-items: center;
  border-radius: 6px;
`;

const TextContainer = styled.div`
    display: flex;
    gap: 5px;
    marginLeft: "auto";
`;

export const SidebarStep: React.FC<SidebarStepProps> = ({
    number,
    name,
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
            <DefaultColoredIcon icon="complete" style={{flexShrink:0}}/>
            <TextContainer>
            <ContentText
                    text={number}
                    style={{userSelect:"none", whiteSpace: "nowrap"}}
                />
            <CollapsibleLabel width={200} isCollapsed={isCollapsed}>
                <ContentText
                    text={name}
                    style={{userSelect:"none", whiteSpace: "nowrap"}}
                />
            </CollapsibleLabel>
            </TextContainer>
            {/* {!isCollapsed && (<TrashButton onClick={handleDelete} isSmall={true} isShy={true} icon={"trash"} style={{marginLeft: "auto"}}/>)} */}
        </StepContainer>
        )
};
