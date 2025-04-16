import { motion } from "framer-motion";
import React, { useState } from "react";
import { styled } from "styled-components";

import SidebarSection from "./sidebar-section/sidebar-section";
import { Section } from "./types";
import { spacing, styledDiv } from "../../theme";
import { Icon } from "../icon/icon";
import { H3 } from "../text";
import { SidebarProps } from "./sidebar.props";
//import { translateGlobalToSectionIndex } from "../../utils/step_index_helper.ts";

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
      {/*eslint-disable-next-line*/}
      {sections &&
        sections.map((section: Section, i: number) => {
          return (
            <SidebarSection
              key={section.id}
              index={i}
              name={section.id}
              title={section.name}
              runName={runName}
              currentSteps={section.steps}
              setCurrentSteps={(updater: any) => setCurrentSteps(i, updater)}
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
