import React, { useState } from "react"
import { styled } from "styled-components";

import { Card } from ".././card"
import SidebarSection from "./sidebar-section/sidebar-section"
//import { SidebarProps } from "./sidebar.props";
import { SectionNames, SelectedStep } from "./types";
import { Icon } from "../icon/icon";


const SidebarContainer = styled.div<{ isCollapsed: boolean }>`
  display: "flex";
  flex-direction: "column";
  padding-right: 10px;
  min-height: 500px;
  border-right: 1px #000 solid;
`;

const SidebarHeader = styled.div<{ isCollapsed: boolean }>`
  display: flex;
  justify-content: ${({ isCollapsed }) => (isCollapsed ? "center" : "flex-end")};
  padding: 8px;
  padding-bottom: 16px;
  cursor: pointer;
`;

export const Sidebar: React.FC<React.HTMLAttributes<HTMLDivElement>> = () => {

  const [isCollapsed, setIsCollapsed] = useState(false)
  const [selectedStep, setSelectedStep] = useState<SelectedStep>({section:"importing", index:0})
  
  const sections:SectionNames[] = ["importing","data_preprocessing","data_analysis","data_integration"]
  const sectionTitles = ["Importing","Data Preprocessing","Data Analysis","Data Integration"]

  const handleClick = () => {
    setIsCollapsed((prev) => !prev)
  }

  return(
    <Card>
        <SidebarContainer isCollapsed={isCollapsed}>
            <SidebarHeader isCollapsed={isCollapsed}>
                <Icon 
                    icon={isCollapsed ? "list" : "chevronDoubleLeft"} 
                    onClick={handleClick}
                />
            </SidebarHeader>
            {sections.map((section:SectionNames, i:number) => {
                    return (
                        <SidebarSection 
                            key={section}
                            name={section} 
                            title={sectionTitles[i]} 
                            index={i} 
                            isCollapsed={isCollapsed}
                            selectedStep={selectedStep}
                            setSelectedStep={setSelectedStep}
                        />  
                    )
            })}
        </SidebarContainer>
    </Card>
  );
};