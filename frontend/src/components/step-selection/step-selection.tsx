import { useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import {
  Button,
  CircularButton,
  GrayButton,
  ToggleableButton,
} from "../button";
import { Modal } from "../modal";
import { StepSelectionProps } from "./step-selection.props.ts";
import { useOutsidePress, useToggleableState } from "../../hooks";
import { color, shadow, size, spacing } from "../../theme";
import { callApi, callApiWithParameters } from "../../utils";
import { iconColor } from "../icon";
import { SectionModes } from "./section-modes.tsx";
import { SectionTitle } from "../section-title";

const sectionModes = {
  [SectionModes.All]: "All available steps",
  [SectionModes.Importing]: "Importing",
  [SectionModes.DataPreprocessing]: "Data Preprocessing",
  [SectionModes.DataAnalysis]: "Data Analysis",
  [SectionModes.DataIntegration]: "Data Integration",
};

const allSteps = "All steps";

export interface StepItem {
  method_name: string;
  section: string;
  display_name: string;
  operation: string;
  method_description: string;
  input_keys: string[];
  output_keys: string[];
}

const fetchStepList = async (): Promise<StepItem[]> => {
  return callApi("step_list/");
};

const WideModal = styled(Modal)`
  width: fit-content;
  max-width: 100%;
  height: fit-content;
  max-height: 100vh;
`;

const BorderDiv = styled.div`
  height: fit-content;
`;

const MakeRowDiv = styled.div`
  width: fit-content;
  display: flex;
  height: 90%;
  max-height: 90vh;
  flex-direction: row;
  padding: ${spacing("medium")};
  gap: ${spacing("medium")};
`;

const SectionSelection = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("smallButtonGap")};
`;

const SectionButton = styled(ToggleableButton)`
  color: ${(props) => (props.isActive ? "white" : "black")};
  justify-content: left;
`;

const StepList = styled.div`
  height: 80vh;
  width: 60vh;
  overflow: hidden;
  overflow-y: auto;
`;

const StepWrapper = styled.div`
  padding: ${spacing("listButtonPadding")};
`;

const LightGrayButton = styled(GrayButton)`
  background-color: ${color("backgroundOffset")};
`;

const HelpButton = styled(Button)`
  background: none;
  width: fit-content;
  &:hover {
    background-color: transparent;
    .icon {
      ${iconColor("protzillaDarkBlue")}
    }
  }

  .icon {
    width: ${size("smallIcon")};
    height: ${size("smallIcon")};
    ${iconColor("protzillaGray")}
  }
`;

const StepDescriptionDropdown = styled.div`
  box-shadow: ${shadow("tooltip")};
  padding: ${spacing("small")};
  max-width: 95%;
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  runName,
  section,
  isSmallButton,

  ...rest
}) => {
  // - - - Step list handling - - -
  const [allStepsList, setAllStepsList] = useState<StepItem[]>([]);
  const [listMode, setListMode] = useState<string>(); // now for operations
  const [activeStepList, setActiveStepList] = useState<StepItem[]>([]);

  useEffect(() => {
    const fetchSteps = async () => {
      const data = await fetchStepList();
      const list = data.filter(
        (step) => (step.section as SectionModes) === section,
      );
      setAllStepsList(list);
    };

    void fetchSteps();
  }, [section]);

  useEffect(() => {
    setActiveStepList(allStepsList);
  }, [allStepsList]);

  useEffect(() => {
    setListMode(allSteps);
  }, [allStepsList]);

  const selectList = (mode: string) => {
    setListMode(mode);
    setActiveStepList(stepsGroupedByOperation[mode]);
  };

  // - - - Step grouping - - -
  const stepsGroupedByOperation = useMemo(() => {
    const result: Record<string, StepItem[]> = {
      [allSteps]: [],
    };

    for (const step of allStepsList) {
      if (!Object.prototype.hasOwnProperty.call(result, step.operation)) {
        result[step.operation] = [];
      }
      result[step.operation].push(step);
      result[allSteps].push(step);
    }

    return result;
  }, [allStepsList]);

  const operationModes: string[] = useMemo(
    () => Object.keys(stepsGroupedByOperation),
    [stepsGroupedByOperation],
  );

  // - - - API calls - - -
  const handleAddStep = async (run_name: string, method_name: string) => {
    await callApiWithParameters("add_step/", {
      run_name: run_name,
      method: method_name,
    });
  };

  // DEBUG - should be deleted before merge
  const continueRunForDebugging = async (run_name: string) => {
    try {
      await callApiWithParameters("continue_run/", { run_name: run_name });
    } catch (error) {
      console.error("Error adding step to workflow:", error);
    }
  };

  // - - - Modal handling - - -
  const [isModalOpen, openModal, closeModal] = useToggleableState(false);
  const refModal = useRef<HTMLDivElement>(null);
  useOutsidePress(refModal, closeModal, isModalOpen, false);

  // - - - Step description dropdown - - -
  const [visibleDescription, setVisibleDescription] = useState<string | null>(
    null,
  );

  // - - - Render - - -
  return (
    <div>
      {isSmallButton ? (
        <CircularButton
          icon={"add"}
          onPress={() => {
            openModal();
            void continueRunForDebugging(runName);
          }}
        />
      ) : (
        <GrayButton
          isShy={true}
          icon={"add"}
          text={"Add steps"}
          onPress={() => {
            openModal();
            void continueRunForDebugging(runName);
          }}
        />
      )}
      <div ref={refModal}>
        <WideModal
          isOpen={isModalOpen}
          onClose={() => {
            closeModal();
            selectList(allSteps);
          }}
          className={""}
          title={"Add steps"}
          {...rest}
        >
          <BorderDiv>
            <MakeRowDiv>
              <SectionSelection>
                {operationModes.map((mode: string) => (
                  <SectionButton
                    key={mode}
                    isActive={listMode === mode}
                    onPress={() => {
                      selectList(mode);
                      setVisibleDescription(null);
                    }}
                    text={mode}
                  ></SectionButton>
                ))}
              </SectionSelection>
              <StepList>
                {allStepsList.length === 0 ? (
                  <SectionTitle baseComponent={"h2"} title={"Loading..."} />
                ) : (
                  <SectionTitle
                    baseComponent={"h2"}
                    title={sectionModes[section]}
                  />
                )}

                {listMode === allSteps ? (
                  Object.keys(stepsGroupedByOperation)
                    .filter((op) => op !== allSteps)
                    .map((operation) => (
                      <div key={operation}>
                        <SectionTitle
                          baseComponent={"h3"}
                          description={operation}
                        ></SectionTitle>
                        <div style={{ padding: "10px 10px 10px 20px" }}>
                          {stepsGroupedByOperation[operation].map(
                            (item, index) => (
                              <StepWrapper key={`step_${String(index)}`}>
                                <LightGrayButton
                                  style={{
                                    textAlign: "left",
                                    justifyContent: "left",
                                  }}
                                  onPress={() =>
                                    void handleAddStep(
                                      runName,
                                      item.method_name,
                                    )
                                  }
                                  key={index}
                                  text={item.display_name}
                                />
                                <HelpButton
                                  icon={"help"}
                                  onPress={() => {
                                    setVisibleDescription(
                                      visibleDescription === item.method_name
                                        ? null
                                        : item.method_name,
                                    );
                                  }}
                                />
                                {visibleDescription === item.method_name && (
                                  <StepDescriptionDropdown>
                                    {item.method_description}
                                  </StepDescriptionDropdown>
                                )}
                              </StepWrapper>
                            ),
                          )}
                        </div>
                      </div>
                    ))
                ) : (
                  <div>
                    <SectionTitle
                      baseComponent={"h3"}
                      description={listMode}
                    ></SectionTitle>
                    <div style={{ padding: "10px 10px 10px 20px" }}>
                      {activeStepList.map((item, index) => (
                        <StepWrapper key={`step_${String(index)}`}>
                          <LightGrayButton
                            style={{
                              textAlign: "left",
                              justifyContent: "left",
                            }}
                            onPress={() =>
                              void handleAddStep(runName, item.method_name)
                            }
                            key={index}
                            text={item.display_name}
                          />
                          <HelpButton
                            icon={"help"}
                            onPress={() => {
                              setVisibleDescription(
                                visibleDescription === item.method_name
                                  ? null
                                  : item.method_name,
                              );
                            }}
                          />
                          {visibleDescription === item.method_name && (
                            <StepDescriptionDropdown>
                              {item.method_description}
                            </StepDescriptionDropdown>
                          )}
                        </StepWrapper>
                      ))}
                    </div>
                  </div>
                )}
              </StepList>
            </MakeRowDiv>
          </BorderDiv>
        </WideModal>
      </div>
    </div>
  );
};
