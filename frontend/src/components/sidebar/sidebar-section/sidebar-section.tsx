import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step"
import { styled } from "styled-components";
import { H3 } from "../../text";
import { useTheme } from "../../../theme";
import { Icon } from "../../icon/icon"
import { useState } from "react"
import { Button } from "../../button";
import React from "react"

const TitleContainer = styled.div<{selected:boolean}>`
  opacity: ${({selected}) => selected ? 1:1};
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
  collapsed,
  selectedStep,
  setSelectedStep
}: SidebarSectionProps) => {
  
  const initialSteps = ["Step1","Step2","Step3"];
  const [steps, setSteps] = useState(initialSteps)
  const [selected,setSelected] = useState(true)

  const handleSelect = () => {
    setTimeout(() => setSelected((prev) => !prev), 50);
  }

  const selectedStepInSection = selectedStep.section === name

  const deleteStep = (index:number) => {
    const newSteps = [...steps]
    newSteps.splice(index,1)
    setSteps(newSteps)
    if (selectedStepInSection) {
      setSelectedStep({
        section: name,
        index: Math.min(selectedStep.index,newSteps.length-1)
      })
    }
  }

  const addStep = () => {
    const newSteps = [...steps]
    newSteps.splice(selectedStep.index+1,0,`new Step ${newSteps.length}`)
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

  if (!collapsed){
    return(
      <SectionContainer>
        <TitleContainer selected={selected} onClick={handleSelect}>
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
              transform: selected? "rotate(180deg)":"rotate(0deg)",
              transition: "transform 0.3s ease"
            }}
          />
        </TitleContainer>
        {selected && steps.map((step,j) => {
            return (
              <SidebarStep 
                text={`${index+1}.${j+1} ${step}`}
                collapsed={collapsed}
                sectionName={name}
                index={j}
                selectedStep={selectedStep}
                setSelectedStep={setSelectedStep}
                deleteStep={deleteStep}
              />
            )
        })}
        {selected && selectedStepInSection && (<Button icon={"add"} text={"add step"} isSmall={true} textStyle={ContentTextStyle} onClick={addStep} style={{margin:"5px", padding:"15px 10px"}} />)}
      </SectionContainer>
    );
  }
  else {
    return (
      <SectionContainer>
        <TitleContainer selected={selected} onClick={handleSelect}>
          <Icon icon={name} style={{width: "30px"}}/>        
        </TitleContainer>
        {selected && steps.map((_, j) => {
            return (
              <SidebarStep 
                text={`${index+1}.${j+1}`} 
                collapsed={collapsed}
                sectionName={name}
                index={j}
                selectedStep={selectedStep}
                setSelectedStep={setSelectedStep}
                deleteStep={deleteStep}
              />
            )
        })}
        {selected && selectedStepInSection && (<Button icon={"add"} isSmall={true} textStyle={ContentTextStyle} onClick={addStep} style={{margin:"5px", padding:"10px"}}/>)}
      </SectionContainer>

    )
  }
  
};

export default SidebarSection;