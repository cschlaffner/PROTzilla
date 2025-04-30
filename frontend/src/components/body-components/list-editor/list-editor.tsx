import React, { useCallback, useEffect, useState } from "react";
import { styled } from "styled-components";

import { ListEditorProps } from "./list-editor.props";
import { color, spacing } from "../../../theme";
import { translateGlobalToSectionIndex } from "../../../utils/step_index_helper.ts";
import { FlexRow } from "../../box";
import { BackendForm } from "../../forms/backend-form/backend-form.tsx";
import { Sidebar } from "../../sidebar";
import { emptySections, Step } from "../../sidebar/types.ts";

const StyledRow = styled(FlexRow)`
  gap: ${spacing("verySmall")};
  align-items: flex-start;
  height: 100%;
`;

const StyledDivider = styled.div`
  width: 1px;
  background-color: ${color("secondary")};
  flex-grow: 1;
  align-self: stretch;
  margin-right: ${spacing("small")};
`;

const StyledFormColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("large")};
  width: 20vw;
  min-width: 250px;
  max-width: 500px;
  padding-top: ${spacing("small")};
  margin: 0 ${spacing("small")};
`;

export const ListEditor: React.FC<ListEditorProps> = ({
  onFormSubmit,
  runName,
  handleStepSelection,
  runData,
}) => {
  const [sections, setSections] = useState(emptySections);

  const setCurrentSteps = (sectionIndex: number, updater: (prevSteps: Step[]) => Step[]) => {
    setSections((prevSections) => {
      return prevSections.map((section, idx) => {
        if (idx === sectionIndex) {
          const updatedSteps = updater(section.steps);
          return { ...section, steps: updatedSteps };
        }
        return section;
      });
    });
  };

  useEffect(() => {
   
    setSections(runData.displayed_steps);
  }, [runData]);

  const currentSection = sections.find(
    (section) => (section.id as string) === runData.current_section,
  );
  // const previousStepSectionIndex = translateGlobalToSectionIndex(
  //   Math.max(runData.current_step_index-1 as number,0),
  //   sections,
  // ).index;

  const stepSectionIndex = translateGlobalToSectionIndex(
    runData.current_step_index,
    sections,
  ).index;

  // const previousStepCalculationStatus =
  //    runData.current_step_index === 0 ? "complete" : currentSection?.steps[previousStepSectionIndex]?.status

  const currentStepCalculationStatus = currentSection?.steps[stepSectionIndex]?.status;

  const buttonText =
    currentStepCalculationStatus === "complete"
      ? "Next"
      : runData.current_section === "importing"
        ? "Import"
        : "Calculate";

  const onNext = () => {
          handleStepSelection(
            translateGlobalToSectionIndex(
              runData.current_step_index + 1,
              sections,
            ),
          );
        }

  const onFormChanged = useCallback(() => {
    let shouldOutdateFollowingStep = false;
    if (currentStepCalculationStatus === "complete") {
      setSections((prevSections) =>
        prevSections.map((section) => {
          if ((section.id as string) === runData.current_section) {
            const updatedSteps = section.steps.map((step, i): Step => {
              if (
                i === stepSectionIndex ||
                (shouldOutdateFollowingStep && (step.status as string) === "complete")
              ) {
                shouldOutdateFollowingStep = true;
                return { ...step, status: "outdated" };
              }
              return step;
            });
            return { ...section, steps: updatedSteps };
          }
          return section;
        }),
      );
    }
  }, [currentStepCalculationStatus, runData.current_section, stepSectionIndex]);

  return (
    <StyledRow>
      <Sidebar
        runName={runName}
        runData={runData}
        sections={sections}
        setCurrentSteps={setCurrentSteps}
        stepSectionIndex={stepSectionIndex}
        handleStepSelection={handleStepSelection}
      />

      <StyledDivider />

      <StyledFormColumn>
        <BackendForm
          runName={runName}
          buttonText={buttonText}
          currentStepCalculationStatus={currentStepCalculationStatus}
          current_step_index={runData.current_step_index}
          onNext={onNext}
          onSubmit={onFormSubmit}
          onChange={onFormChanged}
        />
      </StyledFormColumn>
    </StyledRow>
  );
};
