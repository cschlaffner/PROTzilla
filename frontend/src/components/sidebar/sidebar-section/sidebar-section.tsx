import React, { useState, useRef, useEffect } from "react"
import { styled } from "styled-components";

import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step"
import { useTheme } from "../../../theme";
import { Button } from "../../button";
import { Icon, IconButton } from "../../icon/icon"
import { H3 } from "../../text";
import { CollapsibleLabel } from "../../text-field";
import { motion } from "framer-motion";

const TitleContainer = styled.div`
  display: flex;
  flex-direction: row;
  padding: 5px;
  margin: 5px;
  cursor: pointer;
  align-items: center;
`;

const StepsContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
`;

const SectionContainer = styled.div`
display: flex;
flex-direction: column;
position: relative;

&::before {
  content: "";
  position: absolute;
  left: 5%;
  right: 5%;
  top: 0;
  height: 1px;
  background: linear-gradient(
    to right,
    rgba(200, 200, 200, 0.2) 0%,
    rgba(200, 200, 200, 0.5) 50%,
    rgba(200, 200, 200, 0.2) 100%
  );
}

&:last-child::after {
  display: none; 
}
`;

const SidebarSection: React.FC<SidebarSectionProps> = ({
  name,
  title,
  index,
  isCollapsed,
  selectedStep,
  setSelectedStep
}: SidebarSectionProps) => {
  
  const initialSteps = ["super mega ultra super long step name","Step2","Step3"];
  const [steps, setSteps] = useState(initialSteps)
  const [isSelected,setIsSelected] = useState(true)
  const [handlePosition,setHandlePosition] = useState({top:0, left:0})
  const [hoveredStepIndex,setHoveredStepIndex] = useState(0)
  const [isStepHovered, setIsStepHovered] = useState(false)
  const [isHandleHovered, setIsHandleHovered] = useState(false)

  const handleSelect = () => {
    setTimeout(() => { setIsSelected((prev) => !prev); }, 50);
  }

  const hasSelectedStep = selectedStep.section === name

  const deleteStep = (index:number) => {
    const newSteps = [...steps]
    newSteps.splice(index,1)
    setSteps(newSteps)
    if (hasSelectedStep) {
      setSelectedStep({
        section: name,
        index: Math.min(selectedStep.index,newSteps.length-1)
      })
    }
  }

  const addStep = (index:number) => {
    const newSteps = [...steps]
    newSteps.splice(index+1,0,"new Step")
    setSteps(newSteps)
  }


  const baseTheme = useTheme();
  const ContentTextStyle = {
    "fontSize": baseTheme.fontSizes.h5,
    "lineHeight": baseTheme.fontSizes.h5,
    "fontWeight": baseTheme.fontWeights.medium,
    "whiteSpace": "nowrap"
  }

    return(
      <SectionContainer>
        <TitleContainer onClick={handleSelect}>
          <Icon 
            icon={name}
            style={{flexShrink:0, marginRight:"10px"}}
          />
          <CollapsibleLabel width={"100%"} isCollapsed={isCollapsed}>
            <H3 
              text={title} 
              style={{"userSelect":"none",  "whiteSpace": "nowrap"}}
            />
          </CollapsibleLabel>
          <Icon 
            icon={isSelected ? "chevronDown" : "chevronUp"} 
            style={{flexShrink:0, marginLeft:"2.5px"}}
          />
        </TitleContainer>
        <StepsContainer
          initial={{ height: "auto" }}
          animate={{ height: isSelected ? "auto" : 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          {steps.map((step,j) => {
              const number = `${String(index+1)}.${String(j+1)}`
              return (
                <SidebarStep 
                  key={number}
                  number={number}
                  name={step}
                  isCollapsed={isCollapsed}
                  sectionName={name}
                  sectionLength={steps.length}
                  index={j}
                  selectedStep={selectedStep}
                  setSelectedStep={setSelectedStep}
                  deleteStep={deleteStep}
                  setHandlePosition={setHandlePosition}
                  setIsStepHovered={setIsStepHovered}
                  setHoveredStepIndex={setHoveredStepIndex}
                />
              )
          })}
          {hasSelectedStep && (<Button icon={"add"} text={isCollapsed ? undefined:"add step"} isSmall={false} textStyle={ContentTextStyle} onClick={() => addStep(steps.length)} style={{margin:"5px", padding:`${handlePosition}px`, overflow:"hidden"}} />)}
          
        </StepsContainer>
        {(isStepHovered || isHandleHovered) && (
            <IconButton 
              icon="add" 
              data-group-id="step-group"
              onClick={() => addStep(hoveredStepIndex)}
              onMouseEnter={() => setIsStepHovered(true)}
              onMouseLeave={() => setIsStepHovered(false)}
              style={{
                position: "absolute", 
                left:handlePosition.left, 
                top:handlePosition.top, 
                transform: "translateX(-50%) translateY(-50%)"
              }}
            />
          )}
      </SectionContainer>
    );
  }

export default SidebarSection;