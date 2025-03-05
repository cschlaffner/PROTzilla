import React, { useState } from "react"
import { styled } from "styled-components";

import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step"
import { useTheme } from "../../../theme";
import { Button } from "../../button";
import { Icon } from "../../icon/icon"
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

  const addStep = () => {
    const newSteps = [...steps]
    newSteps.splice(selectedStep.index+1,0,`new Step ${String(newSteps.length)}`)
    setSteps(newSteps)
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    console.log(event)
    if (event.key === 'Delete') {
      deleteStep(index)
    }
  };

  const baseTheme = useTheme();
  const ContentTextStyle = {
    "fontSize": baseTheme.fontSizes.h5,
    "lineHeight": baseTheme.fontSizes.h5,
    "fontWeight": baseTheme.fontWeights.medium,
    "whiteSpace": "nowrap"
  }

    return(
      <SectionContainer onKeyDown={handleKeyDown}>
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
                  key={`step_${number}`}
                  number={number}
                  name={step}
                  isCollapsed={isCollapsed}
                  sectionName={name}
                  index={j}
                  selectedStep={selectedStep}
                  setSelectedStep={setSelectedStep}
                  deleteStep={deleteStep}
                />
              )
          })}
          {hasSelectedStep && (<Button icon={"add"} text={isCollapsed ? undefined:"add step"} isSmall={true} textStyle={ContentTextStyle} onClick={addStep} style={{margin:"5px", padding:"15px 10px", overflow:"hidden"}} />)}
        </StepsContainer>
      </SectionContainer>
    );
  }

export default SidebarSection;