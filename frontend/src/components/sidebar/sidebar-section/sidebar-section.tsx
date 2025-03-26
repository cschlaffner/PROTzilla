import { motion } from "framer-motion";
import React, { useState } from "react";
import { styled } from "styled-components";

import { SidebarSectionProps } from "./sidebar-section.props";
import { SidebarStep } from "./sidebar-step/sidebar-step";
import { useTheme } from "../../../theme";
import { GrayButton } from "../../button";
import { Icon, IconButton } from "../../icon/icon";
import { H3 } from "../../text";
import { CollapsibleLabel } from "../../text-field";
import { callApiWithParameters } from "../../../utils";

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
  const hasSelectedStep = selectedStep.section === name;

  const [currentSteps, setCurrentSteps] = useState(steps);
  const [isMinimized, setIsMinimized] = useState(true);
  const [handlePosition, setHandlePosition] = useState({ top: 0, left: 0 });
  const [hoveredStepIndex, setHoveredStepIndex] = useState(0);
  const [showHandle, setShowHandle] = useState(false);

  //WIP add wont work for now
  const addStep = (index: number) => {
    const newSteps = [...currentSteps];
    newSteps.splice(index + 1, 0, "new Step");
    setCurrentSteps(newSteps);
  };

  const deleteStep = async (index: number) => {
    await callApiWithParameters("delete_step/", {
      run_name: runName,
      section: name,
      index: index.toString(),
    });

    const newSteps = currentSteps;
    newSteps.splice(index, 1);
    setCurrentSteps(newSteps);
    if (hasSelectedStep) {
      setSelectedStep({
        section: name,
        index: Math.min(selectedStep.index, newSteps.length - 1),
      });
    }
  };

  const baseTheme = useTheme();
  const ContentTextStyle = {
    fontSize: baseTheme.fontSizes.h5,
    lineHeight: baseTheme.fontSizes.h5,
    fontWeight: baseTheme.fontWeights.medium,
    whiteSpace: "nowrap",
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
        {currentSteps.map((step: any, j: number) => {
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
        })}
        <GrayButton
          icon={"add"}
          isShy={true}
          color={"protzillaDarkBlue"}
          text={isCollapsed ? undefined : "add step"}
          isSmall={false}
          textStyle={ContentTextStyle}
          onClick={() => {
            addStep(steps.length);
          }}
          style={{
            margin: "0px 5px",
            overflow: "hidden",
          }}
        />
      </StepsContainer>
      {showHandle && steps.length !== 0 && (
        <IconButton
          icon="add"
          data-group-id="step-group"
          onClick={() => {
            addStep(hoveredStepIndex);
          }}
          onMouseEnter={() => {
            setShowHandle(true);
          }}
          onMouseLeave={() => {
            setShowHandle(false);
          }}
          style={{
            position: "absolute",
            left: handlePosition.left,
            top: handlePosition.top,
            transform: "translateX(-50%) translateY(-50%)",
          }}
        />
      )}
    </SectionContainer>
  );
};

export default SidebarSection;
