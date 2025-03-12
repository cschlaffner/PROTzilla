import { motion } from "framer-motion";
import React, { useState } from "react";
import { styled } from "styled-components";

import SidebarSection from "./sidebar-section/sidebar-section";
import { SectionNames, SelectedStep } from "./types";
import { color, spacing } from "../../theme";
import { Icon } from "../icon/icon";
import { H3 } from "../text";

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
