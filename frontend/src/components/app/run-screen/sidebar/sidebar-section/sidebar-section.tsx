import { CollapsibleLabel, H3, Icon } from "@protzilla/core";
import { callApiWithParameters, Step } from "@protzilla/utils";
import { motion } from "framer-motion";
import React, { useState } from "react";
import { styled } from "styled-components";

import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step";
import { StepSelection } from "../../step-selection";

const TitleContainer = styled.div`
  display: flex;
  flex-direction: row;
  padding: 5px;
  margin: 5px;
  cursor: pointer;
  align-items: center;
`;

const StepsContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
`;

const SectionContainer = styled.div`
  display: flex;
  flex-direction: column;
  position: relative;
  margin: 5px 0px;

  &::before {
    content: "";
    position: absolute;
    left: 5%;
    right: 5%;
    top: 0;
    height: 1px;
    background: linear-gradient(
      to right,
      rgba(200, 200, 200, 0.2) 0%,
      rgba(200, 200, 200, 0.5) 50%,
      rgba(200, 200, 200, 0.2) 100%
    );
  }

  &:last-child::after {
    display: none;
  }
`;

const SidebarSection: React.FC<SidebarSectionProps> = ({
  runName,
  name,
  title,
  index,
  isCollapsed,
  stepSectionIndex,
  runData,
  handleStepSelection,
  currentSteps
}: SidebarSectionProps) => {
  const isCurrentSection = runData.current_section === (name as string);

  const [isMinimized, setIsMinimized] = useState(true);
  const [handlePosition, setHandlePosition] = useState({ top: 0, left: 0 });
  const [hoveredStepIndex, setHoveredStepIndex] = useState(0);

  const [showHandle, setShowHandle] = useState(false);

  const addStep = () => {
    handleStepSelection();
  };

  const deleteStep = async (index: number) => {
    await callApiWithParameters("delete_step/", {
      run_name: runName,
      section: name,
      index: index.toString(),
    });
    handleStepSelection();
  };

  return (
    <SectionContainer>
      <TitleContainer
        onClick={() => {
          setIsMinimized((prev) => !prev);
        }}
      >
        <Icon icon={name} style={{ flexShrink: 0, marginRight: "10px" }} />
        <CollapsibleLabel width={"100%"} isCollapsed={isCollapsed}>
          <H3 text={title} style={{ userSelect: "none", whiteSpace: "nowrap" }} />
        </CollapsibleLabel>
        <Icon
          icon={isMinimized ? "chevronDown" : "chevronUp"}
          style={{ flexShrink: 0, marginLeft: "2.5px" }}
        />
      </TitleContainer>
      <StepsContainer
        initial={{ height: "auto" }}
        animate={{ height: isMinimized ? "auto" : 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        {currentSteps.map((step: Step, j: number) => {
          const number = `${String(index + 1)}.${String(j + 1)}`;
          return (
            <SidebarStep
              key={number}
              number={number}
              stepStatus={step.status}
              name={step.method_name + ": " + step.name}
              isCollapsed={isCollapsed}
              sectionName={name}
              sectionLength={currentSteps.length}
              index={j}
              isSelected={isCurrentSection && stepSectionIndex === j}
              handleStepSelection={handleStepSelection}
              deleteStep={() => {
                void deleteStep(j);
              }}
              setHandlePosition={setHandlePosition}
              setShowHandle={setShowHandle}
              setHoveredStepIndex={setHoveredStepIndex}
            />
          );
        })}
        <StepSelection
          runName={runName}
          section={name}
          index={currentSteps.length}
          isSmallButton={false}
          handlePosition={handlePosition}
          onAddStep={addStep}
          setShowHandle={setShowHandle}
        />
      </StepsContainer>
      {showHandle && currentSteps.length !== 0 && (
        <StepSelection
          runName={runName}
          section={name}
          index={hoveredStepIndex}
          isSmallButton={true}
          handlePosition={handlePosition}
          onAddStep={addStep}
          setShowHandle={setShowHandle}
          data-group-id="step-group"
        />
      )}
    </SectionContainer>
  );
};

export default SidebarSection;
