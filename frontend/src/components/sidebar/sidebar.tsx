import { motion } from "framer-motion";
import React, { useState, useEffect } from "react";

import { styled } from "styled-components";
import SidebarSection from "./sidebar-section/sidebar-section";
import { SelectedStep } from "./types";
import { spacing, styledDiv } from "../../theme";
import { Icon } from "../icon/icon";
import { H3 } from "../text";
import { SidebarProps } from "./sidebar.props";
import { callApiWithParameters } from "../../utils";
import { Section, Sections } from "../step-selection/sections.tsx";

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

export const Sidebar: React.FC<SidebarProps> = ({ runName }: SidebarProps) => {
  const emptySections: Section[] = [
    {
      id: Sections.Importing,
      name: "Importing",
      steps: [],
    },
    {
      id: Sections.DataPreprocessing,
      name: "Data Preprocessing",
      steps: [],
    },
    {
      id: Sections.DataAnalysis,
      name: "Data Analysis",
      steps: [],
    },
    {
      id: Sections.DataIntegration,
      name: "Data Integration",
      steps: [],
    },
  ];
  const [sections, setSections] = useState<Section[]>([]);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selectedStep, setSelectedStep] = useState<SelectedStep | null>({
    section: Sections.Importing,
    index: 0,
  });

  useEffect(() => {
    const fetchData = async () => {
      if (runName === "") return;
      const data = await callApiWithParameters("get_run_data/", {
        run_name: runName,
      });
      if (data) {
        const sections = data.data.displayed_steps;
        if (sections.length === 0) {
          setSections(emptySections);
        } else {
          setSections(sections);
        }
      }
    };

    void fetchData();
  }, [runName]);

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
      {sections &&
        sections.map((section: any, i: number) => {
          return (
            <SidebarSection
              runName={runName}
              key={section.id}
              name={section.id}
              title={section.name}
              index={i}
              isCollapsed={isCollapsed}
              selectedStep={selectedStep}
              setSelectedStep={setSelectedStep}
              steps={section.steps}
            />
          );
        })}
    </SidebarContainer>
  );
};
