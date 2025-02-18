import { SidebarStepProps } from "./sidebar-step.props";
import { styled } from "styled-components";
import { H5 } from "../../../text";
import { color } from "../../../../theme"
import { useState } from "react"

// TODOS:
//  -use standard text

const StepContainer = styled.div<{ selected:boolean, collapsed:boolean }>`
  padding: 5px;
  padding-left: ${({collapsed}) => collapsed ? "10px": "35px"};
  background-color:${({selected}) => selected ? color("protzillaLightGray"):""};
  display: flex;
  justify-content: ${({ collapsed }) => (collapsed ? "center" : "left")};
  border-radius: 6px;
`;

export const SidebarStep: React.FC<SidebarStepProps> = ({
    text, 
    collapsed, 
    sectionName, 
    index, 
    selectedStep, 
    setSelectedStep
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
            <H5
                text={text}
                style={{"userSelect":"none"}}
            />
        </StepContainer>
        )
};
