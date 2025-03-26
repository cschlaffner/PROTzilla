import { motion } from "framer-motion";
import React, { useState } from "react";
import { styled } from "styled-components";

import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step";
import { Icon } from "../../icon/icon";
import { H3 } from "../../text";
import { CollapsibleLabel } from "../../text-field";
import { callApiWithParameters } from "../../../utils";
import { StepSelection } from "../../step-selection";
import { Sections } from "../../step-selection/sections.tsx";

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
  selectedStep,
  setSelectedStep,
  steps,
}: SidebarSectionProps) => {
  let hasSelectedStep = selectedStep !== null && selectedStep.section === name;

  const [currentSteps, setCurrentSteps] = useState(steps);
  const [isMinimized, setIsMinimized] = useState(true);
  const [handlePosition, setHandlePosition] = useState({ top: 0, left: 0 });
  const [hoveredStepIndex, setHoveredStepIndex] = useState(0);

  const [showHandle, setShowHandle] = useState(false);

  const updateSteps = async () => {
    const data = await callApiWithParameters("get_run_data/", {
      run_name: runName,
    });
    if (data) {
      if (data.data.displayed_steps.length === 0) {
        setCurrentSteps([]);
      } else {
        setCurrentSteps(data.data.displayed_steps[index].steps);
      }
    }
  };

  const addStep = async () => {
    await updateSteps();
  };

  const deleteStep = async (index: number) => {
    await callApiWithParameters("delete_step/", {
      run_name: runName,
      section: name,
      index: index.toString(),
    });
    await updateSteps();
    if (hasSelectedStep) {
      if (currentSteps.length === 0) {
        hasSelectedStep = false;
        setSelectedStep(null);
      } else {
        setSelectedStep({
          section: name,
          index: Math.min(selectedStep!.index, currentSteps.length - 1),
        });
      }
    }
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
          <H3
            text={title}
            style={{ userSelect: "none", whiteSpace: "nowrap" }}
          />
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
        {currentSteps ? (
          currentSteps.map((step: any, j: number) => {
            const number = `${String(index + 1)}.${String(j + 1)}`;
            return (
              <SidebarStep
                key={number}
                number={number}
                name={step.name}
                isCollapsed={isCollapsed}
                sectionName={name}
                sectionLength={steps.length}
                index={j}
                selectedStep={selectedStep}
                setSelectedStep={setSelectedStep}
                deleteStep={deleteStep}
                setHandlePosition={setHandlePosition}
                setShowHandle={setShowHandle}
                setHoveredStepIndex={setHoveredStepIndex}
              />
            );
          })
        ) : (
          <div></div>
        )}
        <StepSelection
          runName={runName}
          section={name as Sections}
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
          section={name as Sections}
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
