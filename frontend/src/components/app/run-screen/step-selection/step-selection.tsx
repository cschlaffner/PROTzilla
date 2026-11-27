import type { IconType } from "@protzilla/core";
import {
  Button,
  DeleteModal,
  GrayButton,
  Icon,
  IconButton,
  iconColor,
  Modal,
  NameModal,
  SecondaryButton,
  SectionTitle,
  ToggleableButton,
} from "@protzilla/core";
import { useOutsidePress, useToggleableState } from "@protzilla/hooks";
import { color, size, spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters, SectionIDs } from "@protzilla/utils";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { StepSelectionProps } from "./step-selection.props.ts";
import { DOCUMENTATION_URL } from "../../../../constants";

const sectionModes = {
  [SectionIDs.Importing]: "Importing",
  [SectionIDs.DataPreprocessing]: "Data Preprocessing",
  [SectionIDs.DataAnalysis]: "Data Analysis",
  [SectionIDs.DataIntegration]: "Data Integration",
  [SectionIDs.Custom]: "Custom",
};

const allSteps = "All steps";

export interface StepItem {
  method_name: string;
  section: string;
  display_name: string;
  operation: string;
  operation_display_name: string;
  calculation_status: string;
}

interface CustomStepTemplate {
  name: string;
  step_name: string;
}

const documentationPages: Partial<Record<string, string>> = {
  ArbitraryCSVImport: "importing",
  CustomPythonStep: "custom-steps",
  DiannImport: "importing/dia-nn-import",
  FastaImport: "importing/fasta-protein-sequence-import",
  FilterByProteinsCount: "data-preprocessing/filter-samples-proteins-per-sample",
  FilterProteinsByNumberOfValuesPerGroup: "data-preprocessing/filter-proteins-values-per-group",
  ImputationByNormalDistributionSampling:
    "data-preprocessing/imputation-normal-distribution-sampling",
  MetadataColumnAssignment: "importing/metadata-column-assignment",
  MsFraggerImport: "importing/ms-fragger-combined-protein-import",
  NormalisationByTotalSum: "data-preprocessing/normalisation-total-sum",
  PeptideImport: "importing/maxquant-peptide-import",
};

const stepDocumentationUrl = (step: StepItem) => {
  const slug = step.display_name
    .toLowerCase()
    .replace("ptm diff. exp.", "ptm differential expression")
    .replace("diff. expression", "differential expression")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  const page =
    documentationPages[step.method_name] ??
    `${step.section.replace(/_/g, "-")}/${slug}${step.section === "importing" ? "-import" : ""}`;
  return `${DOCUMENTATION_URL}step-documentation/${page}/`;
};

const stepOperationIconMap: Partial<Record<string, string>> = {
  classification: "stepClassification",
  clustering: "stepClustering",
  dimension_reduction: "stepDimensionReduction",
  filter_samples: "stepFilter",
  filter_proteins: "stepFilter",
  filter_peptides: "stepFilter",
  filter_psms: "stepFilter",
  gene_ontology: "stepGO",
  gsea: "stepGSEA",
  imputation: "stepImputation",
  modification_quantification: "stepModificationQuantification",
  normalization: "stepNormalization",
  differential_expression: "stepStatisticalTest",
  transformation: "stepTransformation",
  ptm_visualization: "stepPTMVisualization",
};

const fetchStepList = async (): Promise<StepItem[]> => {
  return callApi("step_list/");
};

const fetchCustomSteps = async (): Promise<CustomStepTemplate[]> => {
  const response = await callApi("custom_steps/");
  return response.data;
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

const CustomStepWrapper = styled(StepWrapper)`
  display: flex;
  align-items: center;
  gap: ${spacing("verySmall")};
`;

const CustomStepActions = styled.div`
  display: flex;
  margin-left: auto;
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

const OperationIconWrapper = styled.div`
  flex-shrink: 0;
  margin-right: 12px;

  /* Targeting the Icon component specifically to make it larger */
  & > svg,
  & > span {
    width: 30px !important;
    height: 30px !important;
  }
`;

export const StepSelection: React.FC<StepSelectionProps> = ({
  runName,
  section,
  isSmallButton = false,
  onAddStep,
  handlePosition = { top: 0, left: 0 },
  setShowHandle = () => undefined,
  ModalTrigger,

  ...rest
}) => {
  // - - -
  const [selectedSection, setSelectedSection] = useState<SectionIDs | null>(null);

  // - - - Step list handling - - -
  const [allStepsList, setAllStepsList] = useState<StepItem[]>([]);
  const [listMode, setListMode] = useState(allSteps);
  const [activeStepList, setActiveStepList] = useState<StepItem[]>([]);
  const [customSteps, setCustomSteps] = useState<CustomStepTemplate[]>([]);
  const [customStepToRename, setCustomStepToRename] = useState<CustomStepTemplate | null>(null);
  const [customStepToDelete, setCustomStepToDelete] = useState<CustomStepTemplate | null>(null);

  useEffect(() => {
    if (!selectedSection) return;
    const fetchSteps = async () => {
      const data = await fetchStepList();
      const list = data.filter((step) => (step.section as SectionIDs) === section);
      list.sort((a, b) => a.display_name.localeCompare(b.display_name));
      setAllStepsList(list);
    };

    void fetchSteps();
  }, [selectedSection, section]);

  useEffect(() => {
    setActiveStepList(allStepsList);
  }, [allStepsList, section]);

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

    const sortedSteps = allStepsList.sort((a, b) => {
      if (a.operation === b.operation) {
        return a.display_name.localeCompare(b.display_name);
      }
      return a.operation.localeCompare(b.operation);
    });
    for (const step of sortedSteps) {
      if (!Object.prototype.hasOwnProperty.call(result, step.operation)) {
        result[step.operation] = [];
      }
      result[step.operation].push(step);
      result[allSteps].push(step);
    }

    return result;
  }, [allStepsList]);

  const operationModes: string[] = useMemo(
    () => Object.keys(stepsGroupedByOperation).sort(),
    [stepsGroupedByOperation],
  );

  const operationTitle = (operation: string) =>
    section === SectionIDs.Custom && operation === "others"
      ? "Create blank Step"
      : stepsGroupedByOperation[operation][0].operation_display_name;

  // - - - API calls - - -
  const handleAddStep = async (run_name: string, method_name: string) => {
    await callApiWithParameters("add_step/", {
      run_name: run_name,
      method: method_name,
    }).then(() => {
      onAddStep();
    });
  };

  const updateCustomStep = async (action: string, name: string, new_name = "") => {
    const response = await callApiWithParameters("custom_steps/", {
      action,
      name,
      new_name,
      run_name: runName,
    });
    if (!response.success) return;
    if (action === "add") onAddStep();
    else setCustomSteps(await fetchCustomSteps());
  };

  // - - - Modal handling - - -
  const [isModalOpen, openModal, closeModal] = useToggleableState(false);
  const refModal = useRef<HTMLDivElement>(null);
  useOutsidePress(refModal, closeModal, isModalOpen, false);

  const handleOpenModal = () => {
    openModal();
    setSelectedSection(section);
    if (section === SectionIDs.Custom) void fetchCustomSteps().then(setCustomSteps);
  };

  // - - - Render - - -
  return (
    <div style={{ display: "flex", flexDirection: "column", margin: "0 5px" }}>
      {ModalTrigger ? (
        ModalTrigger(handleOpenModal)
      ) : isSmallButton ? (
        <IconButton
          icon={"add"}
          onPointerDown={isModalOpen ? undefined : handleOpenModal}
          style={{
            position: "absolute",
            left: handlePosition.left,
            top: handlePosition.top,
            transform: "translateX(-50%) translateY(-50%)",
          }}
          onMouseEnter={() => {
            setShowHandle(true);
          }}
        />
      ) : (
        <GrayButton
          color={"protzillaDarkBlue"}
          isShy={true}
          icon={"add"}
          text={"Add steps"}
          onPointerDown={() => {
            openModal();
            handleOpenModal();
          }}
          style={{
            display: "flex",
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
                {operationModes.map((mode: string) => {
                  const buttonLabel = mode === "All steps" ? "All Steps" : operationTitle(mode);
                  return (
                    <SectionButton
                      key={mode}
                      isActive={listMode === mode}
                      onPress={() => {
                        selectList(mode);
                      }}
                      text={buttonLabel}
                    ></SectionButton>
                  );
                })}
              </SectionSelection>
              <div>
                {allStepsList.length === 0 ? (
                  <SectionTitle baseComponent={"h2"} title={"Loading..."} />
                ) : (
                  <SectionTitle
                    baseComponent={"h2"}
                    title={sectionModes[section]}
                    // style={{ paddingLeft: "100px" }}
                  />
                )}
                <StepList>
                  {listMode === allSteps ? (
                    Object.keys(stepsGroupedByOperation)
                      .filter((op) => op !== allSteps)
                      .map((operation) => {
                        const icon = stepOperationIconMap[operation] ?? (section as IconType);
                        const title = operationTitle(operation);

                        return (
                          <div key={operation}>
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                              <OperationIconWrapper>
                                <Icon icon={icon as IconType} />
                              </OperationIconWrapper>
                              <SectionTitle baseComponent={"h3"} description={title} />
                            </div>
                            <div style={{ padding: "10px 10px 10px 20px" }}>
                              {stepsGroupedByOperation[operation].map((item, index) => (
                                <StepWrapper key={`step_${String(index)}`}>
                                  <LightGrayButton
                                    style={{
                                      textAlign: "left",
                                      justifyContent: "left",
                                    }}
                                    onPress={() => void handleAddStep(runName, item.method_name)}
                                    key={index}
                                    text={item.display_name}
                                  />
                                  <HelpButton
                                    icon={"help"}
                                    onPress={() => window.open(stepDocumentationUrl(item))}
                                  />
                                </StepWrapper>
                              ))}
                            </div>
                          </div>
                        );
                      })
                  ) : (
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <OperationIconWrapper>
                          <Icon icon={(stepOperationIconMap[listMode] ?? section) as IconType} />
                        </OperationIconWrapper>
                        <SectionTitle
                          baseComponent={"h3"}
                          description={operationTitle(listMode)}
                        ></SectionTitle>
                      </div>
                      <div style={{ padding: "10px 10px 10px 20px" }}>
                        {activeStepList.map((item, index) => (
                          <StepWrapper key={`step_${String(index)}`}>
                            <LightGrayButton
                              style={{
                                textAlign: "left",
                                justifyContent: "left",
                              }}
                              onPress={() => void handleAddStep(runName, item.method_name)}
                              key={index}
                              text={item.display_name}
                            />
                            <HelpButton
                              icon={"help"}
                              onPress={() => window.open(stepDocumentationUrl(item))}
                            />
                          </StepWrapper>
                        ))}
                      </div>
                    </div>
                  )}
                  {section === SectionIDs.Custom && customSteps.length > 0 && (
                    <div>
                      <SectionTitle baseComponent={"h3"} description={"Saved custom steps"} />
                      {customSteps.map((template) => (
                        <CustomStepWrapper key={template.name}>
                          <LightGrayButton
                            onPress={() => void updateCustomStep("add", template.name)}
                            text={template.step_name}
                          />
                          <CustomStepActions>
                            <SecondaryButton
                              isSmall={true}
                              isShy={true}
                              onPress={() => {
                                setCustomStepToRename(template);
                              }}
                            >
                              <Icon icon={"edit"} style={{ height: "15px" }} />
                            </SecondaryButton>
                            <SecondaryButton
                              isSmall={true}
                              isShy={true}
                              isCautious={true}
                              onPress={() => {
                                setCustomStepToDelete(template);
                              }}
                            >
                              <Icon icon={"trash"} style={{ height: "15px" }} />
                            </SecondaryButton>
                          </CustomStepActions>
                        </CustomStepWrapper>
                      ))}
                    </div>
                  )}
                </StepList>
              </div>
            </MakeRowDiv>
          </BorderDiv>
        </WideModal>
        <NameModal
          title="Rename custom step"
          label="With custom step name:"
          submitLabel="Rename custom step"
          initialValue={customStepToRename?.step_name}
          isOpen={customStepToRename !== null}
          onClose={() => {
            setCustomStepToRename(null);
          }}
          onSubmit={(name) => {
            if (customStepToRename) void updateCustomStep("rename", customStepToRename.name, name);
            setCustomStepToRename(null);
          }}
        />
        <DeleteModal
          title={`Delete custom step "${customStepToDelete?.step_name ?? ""}"?`}
          isOpen={customStepToDelete !== null}
          onClose={() => {
            setCustomStepToDelete(null);
          }}
          onConfirm={() => {
            if (customStepToDelete) void updateCustomStep("delete", customStepToDelete.name);
            setCustomStepToDelete(null);
          }}
        />
      </div>
    </div>
  );
};
