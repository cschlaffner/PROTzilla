import { motion } from "framer-motion";
import React, { useState, useEffect } from "react"
import { styled } from "styled-components";

import SidebarSection from "./sidebar-section/sidebar-section";
import { SectionNames, SelectedStep } from "./types";
import { spacing } from "../../theme";
import { Icon } from "../icon/icon";
import { H3 } from "../text";
import { SidebarProps } from "./sidebar.props";
import { callApiWithParameters } from "../../utils";



const SidebarContainer = styled(motion.div)`
  position: relative;
  display: "flex";
  flex-direction: "column";
  padding: 0px 3px;
  width: 100%;
  overflow: hidden;
`;

const SidebarHeader = styled.div<{ isCollapsed: boolean }>`
  display: flex;
  justify-content: left;
  padding: ${spacing("small")};
  cursor: pointer;
`;

export const Sidebar: React.FC<SidebarProps> = ({runName}:SidebarProps) => {

  const sections: SectionNames[] = ["importing", "data_preprocessing", "data_analysis", "data_integration"]
  const sectionTitles = ["Importing", "Data Preprocessing", "Data Analysis", "Data Integration"]

  useEffect(() => {
      console.log(runName)
      const fetchData = async () => {
        if (runName="") return;
         //const asd = await callApi("run_information");
        const data = await callApiWithParameters("get_run_data/",{run_name:runName});
        if (data) {
          console.log(data);
        }
      };
  
      void fetchData();
    }, []);

  const [isCollapsed, setIsCollapsed] = useState(false)
  const [selectedStep, setSelectedStep] = useState<SelectedStep>({section: "importing", index: 0})
  

  return (
    <SidebarContainer
      initial={{ width: 300 }}
      animate={{ width: isCollapsed ? 77.5 : 300 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      <SidebarHeader isCollapsed={isCollapsed}>
        {!isCollapsed && <H3>List</H3>}
        <Icon
          icon={isCollapsed ? "list" : "chevronDoubleLeft"}
          onClick={() => {
            setIsCollapsed((prev) => !prev);
          }}
          style={{ marginLeft: isCollapsed ? "0" : "auto" }}
        />
      </SidebarHeader>
      {sections.map((section: SectionNames, i: number) => {
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
        );
      })}
    </SidebarContainer>
  );
};
