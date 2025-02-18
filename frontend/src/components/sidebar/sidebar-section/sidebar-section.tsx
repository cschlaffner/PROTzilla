import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step"
import { styled } from "styled-components";
import { H3 } from "../../text";
import { Icon } from "../../icon/icon"
import { useState } from "react"

// TODOS:
//  -change line color,thickness
//  -use standard text

const TitleContainer = styled.div`
  display: flex;
  flex-direction: row;
  margin: 10px;
  cursor: pointer;
  gap: 10px
`;

const SidebarSection: React.FC<SidebarSectionProps> = ({
  name,
  title,
  index,
  collapsed,
  selectedStep,
  setSelectedStep
}: SidebarSectionProps) => {
  
  const [selected,setSelected] = useState(true)

  const steps = ["Step1","Step2","Step3"];

  const handleSelect = () => {
    setSelected(!selected)
  }

  const SectionContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding-bottom: ${selected ? 10 : 0}px;
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
        <TitleContainer onClick={handleSelect}>
          <Icon 
            icon={name}
          />
          <H3 
            text={title} 
            style={{"userSelect":"none"}}
          />
          <Icon 
            icon={selected ? "chevronUp" : "chevronDown"} 
            style={{marginLeft: "auto", width: "30px"}}
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
              />
            )
        })}
      </SectionContainer>
    );
  }
  else {
    return (
      <SectionContainer>
        <TitleContainer>
          <Icon icon={name} style={{width: "30px"}}/>        
        </TitleContainer>
        {steps.map((_, j) => {
            return (
              <SidebarStep 
                text={`${index+1}.${j+1}`} 
                collapsed={collapsed}
                sectionName={name}
                index={j}
                selectedStep={selectedStep}
                setSelectedStep={setSelectedStep}
              />
            )
        })}
      </SectionContainer>

    )
  }
  
};

export default SidebarSection;