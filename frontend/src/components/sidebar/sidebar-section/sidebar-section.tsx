import React, { useState } from "react"
import { styled } from "styled-components";

import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step"
import { useTheme } from "../../../theme";
import { Button } from "../../button";
import { Icon } from "../../icon/icon"
import { H3 } from "../../text";

const TitleContainer = styled.div<{isSelected:boolean}>`
  opacity: ${({isSelected}) => isSelected ? 1:1};
  display: flex;
  flex-direction: row;
  margin: 10px;
  cursor: pointer;
  gap: 10px;
  justify-content: center;
  transition: opacity 0.3s ease;
`;

const SidebarSection: React.FC<SidebarSectionProps> = ({
  name,
  title,
  index,
  isCollapsed,
  selectedStep,
  setSelectedStep
}: SidebarSectionProps) => {
  
  const initialSteps = ["Step1","Step2","Step3"];
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

  const baseTheme = useTheme();
  const ContentTextStyle = {
    "fontSize": baseTheme.fontSizes.h5,
    "lineHeight": baseTheme.fontSizes.h5,
    "fontWeight": baseTheme.fontWeights.medium
  }

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

  if (!isCollapsed){
    return(
      <SectionContainer>
        <TitleContainer isSelected={isSelected} onClick={handleSelect}>
          <Icon 
            icon={name}
          />
          <H3 
            text={title} 
            style={{"userSelect":"none"}}
          />
          <Icon 
            icon={"chevronUp"} 
            style={{
              marginLeft: "auto",
              width: "30px",
              transform: isSelected? "rotate(180deg)":"rotate(0deg)",
              transition: "transform 0.3s ease"
            }}
          />
        </TitleContainer>
        {isSelected && steps.map((step,j) => {
            const number = `${String(index+1)}.${String(j+1)}`
            return (
              <SidebarStep 
                key={`step_${number}`}
                text={`${number} ${step}`}
                isCollapsed={isCollapsed}
                sectionName={name}
                index={j}
                selectedStep={selectedStep}
                setSelectedStep={setSelectedStep}
                deleteStep={deleteStep}
              />
            )
        })}
        {isSelected && hasSelectedStep && (<Button icon={"add"} text={"add step"} isSmall={true} textStyle={ContentTextStyle} onClick={addStep} style={{margin:"5px", padding:"15px 10px"}} />)}
      </SectionContainer>
    );
  }
  else {
    return (
      <SectionContainer>
        <TitleContainer isSelected={isSelected} onClick={handleSelect}>
          <Icon icon={name} style={{width: "30px"}}/>        
        </TitleContainer>
        {isSelected && steps.map((_, j) => {
            const number = `${String(index+1)}.${String(j+1)}`
            return (
              <SidebarStep 
                key={`step_${number}`}
                text={number}
                isCollapsed={isCollapsed}
                sectionName={name}
                index={j}
                selectedStep={selectedStep}
                setSelectedStep={setSelectedStep}
                deleteStep={deleteStep}
              />
            )
        })}
        {isSelected && hasSelectedStep && (<Button icon={"add"} isSmall={true} textStyle={ContentTextStyle} onClick={addStep} style={{margin:"5px", padding:"10px"}}/>)}
      </SectionContainer>

    )
  }
  
};

export default SidebarSection;