import { motion } from "framer-motion";
import React, { useState } from "react";
import { styled } from "styled-components";

import SidebarSection from "./sidebar-section/sidebar-section";
import { SectionNames, SelectedStep } from "./types";
import { Icon } from "../icon/icon";

const SidebarContainer = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  display: "flex";
  flex-direction: "column";
  padding: 0px 3px;
  border-right: 1px #000 solid;
  overflow: hidden;
`;

const SidebarHeader = styled.div<{ isCollapsed: boolean }>`
  display: flex;
  justify-content: ${({ isCollapsed }) => (isCollapsed ? "left" : "flex-end")};
  padding: 5px;
  margin: 5px;
  cursor: pointer;
`;

export const Sidebar: React.FC<React.HTMLAttributes<HTMLDivElement>> = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selectedStep, setSelectedStep] = useState<SelectedStep>({
    section: "importing",
    index: 0,
  });

  const sections: SectionNames[] = [
    "importing",
    "data_preprocessing",
    "data_analysis",
    "data_integration",
  ];
  const sectionTitles = [
    "Importing",
    "Data Preprocessing",
    "Data Analysis",
    "Data Integration",
  ];

  return (
    <SidebarContainer
      initial={{ width: 300 }}
      animate={{ width: isCollapsed ? 77.5 : 300 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      <SidebarHeader isCollapsed={isCollapsed}>
        <Icon
          icon={isCollapsed ? "list" : "chevronDoubleLeft"}
          onClick={() => {
            setIsCollapsed((prev) => !prev);
          }}
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
