import { H3, Icon } from "@protzilla/core/shared";
import { spacing, styledDiv } from "@protzilla/theme";
import { Section, Step } from "@protzilla/utils";
import { motion } from "framer-motion";
import React, { useState } from "react";
import { styled } from "styled-components";

import SidebarSection from "./sidebar-section/sidebar-section";
import { SidebarProps } from "./sidebar.props";

const SidebarContainer = styled(motion.div)`
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0px 3px;
  width: 100%;
  overflow: hidden;
`;

const SidebarHeader = styledDiv.div<{ isCollapsed: boolean }>`
  display: flex;
  justify-content: left;
  padding: ${spacing("small")};
  cursor: pointer;
`;

export const Sidebar: React.FC<SidebarProps> = ({
  runName,
  runData,
  sections,
  setCurrentSteps,
  stepSectionIndex,
  handleStepSelection,
}: SidebarProps) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

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
      {sections.map((section: Section, i: number) => {
        return (
          <SidebarSection
            key={section.id}
            index={i}
            name={section.id}
            title={section.name}
            runName={runName}
            currentSteps={section.steps}
            setCurrentSteps={(updater: (prevSteps: Step[]) => Step[]) => {
              setCurrentSteps(i, updater);
            }}
            isCollapsed={isCollapsed}
            stepSectionIndex={stepSectionIndex}
            runData={runData}
            handleStepSelection={handleStepSelection}
          />
        );
      })}
    </SidebarContainer>
  );
};
