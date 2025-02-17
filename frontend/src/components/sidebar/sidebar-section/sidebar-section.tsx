import React from "react"

import { SidebarSectionProps } from "./sidebar-section.props";
import { Icon } from "../../icon/icon"


const SidebarSection: React.FC<SidebarSectionProps> = ({name}: SidebarSectionProps) => {
  const steps: any = [];
  return(
    <>
    <Icon icon={name}></Icon>
    {steps.map((step:any) => {
        return (<></>)
    })}
    </>
  );
};

export default SidebarSection;