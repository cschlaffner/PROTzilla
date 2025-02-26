import { SidebarStepProps } from "./sidebar-step.props";
import { styled } from "styled-components";
import { ContentText } from "../../../text";
import { color } from "../../../../theme"
import { useState } from "react"
import { DefaultColoredIcon } from "../../../icon/icon"
import { TrashButton } from "../../../button";

// TODOS:
//  -use standard text

const StepContainer = styled.div<{ selected:boolean, collapsed:boolean }>`
  margin: 0 5px;  
  gap:10px;
  padding: 5px;
  background-color:${({selected}) => selected ? color("protzillaLightGray"):""};
  display: flex;
  justify-content: ${({ collapsed }) => (collapsed ? "center" : "left")};
  align-items: center;
  border-radius: 6px;
`;

export const SidebarStep: React.FC<SidebarStepProps> = ({
    text,
    collapsed,
    sectionName,
    index,
    selectedStep,
    setSelectedStep,
    deleteStep
}: SidebarStepProps) => {

    const [dragging, setDragging] = useState(false)

    const handleClick = () => {
        setSelectedStep({
            section: sectionName,
            index: index
        })
    }

    const handleDragStart = () => {
        setDragging(true)
    }

    const handleDragEnd = () => {
        setDragging(false)
    }

    const handleDelete = (event: React.MouseEvent) => {
        event.stopPropagation()
        deleteStep(index)
    }

    const selected =
        selectedStep.section === sectionName &&
        selectedStep.index === index

    return(
        <StepContainer
            draggable
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            onClick={handleClick}
            selected={selected}
            collapsed={collapsed}
        >
            <DefaultColoredIcon icon="complete"/>
            <ContentText
                text={text}
                style={{"userSelect":"none"}}
            />
            {!collapsed && (<TrashButton onClick={handleDelete} isSmall={true} isShy={true} icon={"trash"} style={{marginLeft: "auto"}}/>)}
        </StepContainer>
        )
};
