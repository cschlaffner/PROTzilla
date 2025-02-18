import React from "react"
import { Card } from ".././card"
import { styled } from "styled-components";
import SidebarSection from "./sidebar-section/sidebar-section"
import { SidebarProps } from "./sidebar.props";
import { Icon } from "../icon/icon";
import { useState } from "react"
import { SelectedStep } from "./types";


const SidebarContainer = styled.div`
  display: "flex";
  flex-direction: "column";
  padding-right: 10px;
  min-height: 500px;
  border-right: 2px #000 solid;
`;

const SidebarHeader = styled.div<{ collapsed: boolean }>`
  display: flex;
  justify-content: ${({ collapsed }) => (collapsed ? "center" : "flex-end")};
  padding: 8px;
  padding-bottom: 16px;
  cursor: pointer;
`;

export const Sidebar: React.FC<SidebarProps> = ({}: SidebarProps) => {

  const [collapsed, setCollapsed] = useState(false)
  const [selectedStep, setSelectedStep] = useState<SelectedStep>({section:"importing", index:0})
  
  const sections = ["importing","data_preprocessing","data_analysis","data_integration"]
  const sectionTitles = ["Importing","Data Preprocessing","Data Analysis","Data Integration"]

  const handleClick = () => {
    setCollapsed(!collapsed)
  }

  return(
    <Card>
        <SidebarContainer>
            <SidebarHeader collapsed={collapsed}>
                <Icon 
                    icon={collapsed ? "list" : "chevronDoubleLeft"} 
                    onClick={handleClick}
                />
            </SidebarHeader>
            {sections.map((section:any, i:number) => {
                    return (
                        <SidebarSection 
                            name={section} 
                            title={sectionTitles[i]} 
                            index={i} 
                            collapsed={collapsed}
                            selectedStep={selectedStep}
                            setSelectedStep={setSelectedStep}
                        />  
                    )
            })}
        </SidebarContainer>
    </Card>
  );
};