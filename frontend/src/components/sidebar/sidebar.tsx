import React from "react"

import SidebarSection from "./sidebar-section/sidebar-section"
import { SidebarProps } from "./sidebar.props";

export const Sidebar: React.FC<SidebarProps> = ({}: SidebarProps) => {
  
  const sections:any = ["importing","data_preprocessing","data_analysis","data_integration"]  
  return(
    <div style={{width: "200px", display: "flex", flexDirection: "column"}}>
      {sections.map((section:any) => {
          return (<SidebarSection name={section}></SidebarSection>)
      })}
    </div>
  );
};