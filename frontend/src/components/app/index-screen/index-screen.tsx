import { Navbar, RunsTable, useNotification } from "@protzilla/app";
import {
  Button,
  Card,
  Form,
  InputValueType,
  Modal,
  SearchInputField,
  SecondaryButton,
  SectionTitle,
  TagMenu,
  Workflow,
} from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { size, spacing, styledDiv } from "@protzilla/theme";
import { callApi, callApiWithParameters, Run } from "@protzilla/utils";
import saveAs from "file-saver";
import React, { useCallback, useEffect, useState } from "react";
import { Container } from "react-grid-system";
import { useNavigate } from "react-router-dom";
import { styled, useTheme } from "styled-components";
import "bootstrap/dist/css/bootstrap.min.css";

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const StyledHeader = styledDiv.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`;

const StyledButtonDiv = styledDiv.div`
  position: relative;
  width: calc(2 * ${size("buttonHeight")} + ${spacing("buttonGap")})
`;

const StyledLeftButton = styled(Button)`
  position: absolute;
  top: 0px;
  left: 0px;
`;

const StyledRightButton = styled(Button)`
  position: absolute;
  top: 0px;
  left: calc(${size("buttonHeight")} + ${spacing("buttonGap")});
`;

const StyledContainer = styled.div`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-grow: 1;
  flex-direction: column;
  box-sizing: border-box;
`;

const StyledWorkflowContainer = styled(Container)`
  display: flex;
  overflow-x: auto;

  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }
`;

const StyledTemplateCard = styled(Card)`
  height: ${size("templateSelectionHeight")};
  width: calc(100vw - (2 * ${spacing("small")}));
`;

const NavigationDiv = styledDiv.div`
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: ${spacing("small")};
`;

const StyledArrowButton = styled(SecondaryButton)`
  height: 10px;
  padding-left: ${spacing("small")};
  padding-right: ${spacing("small")};
`;
const StyledRunSelectionCard = styled(Card)`
  min-height: ${size("runSelectionMinHeight")};
  height: calc(
    100vh - ${spacing("navbarHeight")} - ${size("templateSelectionHeight")} -
      (3 * ${spacing("small")})
  );
  width: calc(100vw - (2 * ${spacing("small")}));
  box-sizing: border-box;

  overflow-y: auto;
`;

const StyledDiv = styledDiv.div`
  display: flex;
  flex-direction: row;
`;

export const IndexScreen: React.FC = () => {
  const navigate = useNavigate();
  const notify = useNotification();
  const theme = useTheme();

  const [workflows, setWorkflows] = useState<string[]>([]);
  const [searchTermTop, setSearchTermTop] = useState<string>("");
  const [searchTermRuns, setSearchTermRuns] = useState<string>("");
  const [isWorkflowModalOpen, setIsWorkflowModalOpen] = useState(false);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);
  const [isExportRunModalOpen, openExportRunModal, closeExportRunModal] = useToggleableState(false);
  const [isImportRunModalOpen, openImportRunModal, closeImportRunModal] = useToggleableState(false);
  const [isExportModalOpen, openExportModal, closeExportModal] = useToggleableState(false);
  const [isImportModalOpen, openImportModal, closeImportModel] = useToggleableState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState("");
  const [runs, setRuns] = useState<Run[]>([] as Run[]);
  //lazy initialization to prevent .map() error
  const [selectedRun, setSelectedRun] = useState<Run>(() => ({
    run_name: "",
    creation_date: "",
    modification_date: "",
    memory_mode: "",
    run_steps: [],
    favourite_status: false,
    run_tags: [],
  }));

  const getRuns = async () => {
    const response = await callApi("run_information/");
    if (response.success) {
      setRuns(response.data[0]);
    } else {
      notify({
        title: "Error",
        message: response.message,
        type: "error",
      });
    }
  };

  useEffect(() => {
    void getRuns();
    //only needed initially - functions that update runs will fetch them, too
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getWorkflows = async () => {
    const data = await callApi("workflow_name_list/");
    if (data) {
      setWorkflows(data);
    }
  };

  useEffect(() => {
    void getWorkflows();
  }, []);

  const filteredWorkflows = workflows.filter((workflow) =>
    workflow.toLowerCase().includes(searchTermTop.toLowerCase()),
  );

  const workflowOptions =
    workflows.length > 0
      ? workflows
          .sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }))
          .map((workflow) => ({
            label: workflow,
            value: workflow,
          }))
      : [{ label: "No workflows available", value: "" }];

  const filteredRuns = runs.filter(
    (run) =>
      run.run_name.toLowerCase().includes(searchTermRuns.toLowerCase()) ||
      run.modification_date.toLowerCase().includes(searchTermRuns.toLowerCase()) ||
      run.run_tags.some((tag) => tag.toLowerCase().includes(searchTermRuns.toLowerCase())) ||
      run.run_steps.some((step) => step.toLowerCase().includes(searchTermRuns.toLowerCase())),
  );

  const handleAddTag = (tag: string) => {
    void callApiWithParameters("add_tag/", {
      run_name: selectedRun.run_name,
      tag_name: tag,
    });
    const updated = runs.map((run) =>
      run.run_name === selectedRun.run_name ? { ...run, run_tags: [...run.run_tags, tag] } : run,
    );
    setRuns(updated);
  };

  const handleDeleteTag = (tagToDelete: string) => {
    void callApiWithParameters("delete_tag/", {
      run_name: selectedRun.run_name,
      tag_name: tagToDelete,
    });
    setRuns((runs) =>
      runs.map((run) =>
        run.run_name === selectedRun.run_name
          ? {
              ...run,
              run_tags: run.run_tags.filter((tag) => tag !== tagToDelete),
            }
          : run,
      ),
    );
    setSelectedRun((run) => ({
      ...run,
      run_tags: run.run_tags.filter((tag) => tag !== tagToDelete),
    }));
  };

  const handleContinueRun = useCallback(
    (data: Record<string, InputValueType>) => {
      const runName = data.runname;
      if (!runName) {
        notify({
          title: "Error",
          message: "Please enter a run name.",
          type: "error",
        });
        return;
      }
      void callApiWithParameters("add_run/", {
        run_name: runName,
        workflow_name: data.workflow ?? "",
        df_mode_name: data.df_mode ?? "disk",
      }).then(() => {
        notify({
          title: "Run created",
          message: `Run ${String(data.runname)} has been created`,
          type: "success",
        });

        void callApiWithParameters("continue_run/", {
          run_name: runName as string,
        }).then(() => {
          void navigate("/run", { state: { runName } });
        });
      });
    },
    [notify, navigate],
  );

  const handleExportRun = async (runName: InputValueType) => {
    const blob: Blob = await callApiWithParameters(
      "export_run/",
      { run_name: runName ?? "placeholder" },
      "blob",
    );
    saveAs(blob, (runName ?? "placeholder").toString() + ".zip");
    notify({
      title: "Exported successfully",
      message: `Run ${String(runName)} has been exported`,
      type: "success",
    });
  };

  const handleImportRun = async (runName: InputValueType) => {
    const response = await callApiWithParameters("import_run/", {
      run_file: runName ?? "",
    });
    if (response.success) {
      notify({
        title: "Imported successfully",
        message: `Run ${String(runName)} has been imported`,
        type: "success",
      });
      void getRuns();
    } else {
      notify({
        title: "Something went wrong",
        message: String(response.message),
        type: "error",
      });
    }
  };
  const handleExportWorkflow = async (workflowName: InputValueType) => {
    const blob: Blob = await callApiWithParameters(
      "export_workflow/",
      { workflow_name: workflowName ?? "standard" },
      "blob",
    );
    saveAs(blob, (workflowName ?? "standard").toString() + ".yaml");
    notify({
      title: "Exported successfully",
      message: `Workflow ${String(workflowName)} has been exported`,
      type: "success",
    });
  };
  const workflowContainerSize = parseInt(
    (theme.sizes.bigButtonContainerDimension as unknown as string).replace("px", ""),
  );

  const handleImportWorkflow = async (workflow: InputValueType, newName: InputValueType) => {
    const response = await callApiWithParameters("import_workflow/", {
      workflow_file: workflow ?? "",
      new_name: newName ?? "",
    });
    if (response.success) {
      notify({
        title: "Imported successfully",
        message: `Workflow ${String(workflow)} has been imported as ${newName == "" ? String(workflow).replace(".yaml", "") : String(newName)}`,
        type: "success",
      });
      void getWorkflows();
    } else {
      notify({
        title: "Something went wrong :(",
        message: response.message,
        type: "error",
      });
    }
  };

  const scrollLeft = () => {
    const container = document.querySelector(".workflow-container");
    if (container) {
      container.scrollLeft -= workflowContainerSize;
    }
  };

  const scrollRight = () => {
    const container = document.querySelector(".workflow-container");
    if (container) {
      container.scrollLeft += workflowContainerSize;
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <StyledNavbar
        showRunInformation={false}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => void navigate("/")}
      />

      <StyledContainer>
        <StyledTemplateCard
          title={
            <StyledHeader>
              Template Workflows
              <StyledButtonDiv>
                <StyledLeftButton
                  onClick={() => {
                    openExportModal();
                  }}
                  icon="download"
                  tooltip="Export a workflow"
                  tooltipPosition={"left"}
                ></StyledLeftButton>
                <StyledRightButton
                  onClick={() => {
                    openImportModal();
                  }}
                  icon="upload"
                  tooltip="Import a workflow"
                  tooltipPosition={"left"}
                ></StyledRightButton>
              </StyledButtonDiv>
            </StyledHeader>
          }
        >
          <SearchInputField
            style={{ padding: "0", gap: "0", width: "30%" }}
            value={searchTermTop}
            onChange={(e) => {
              setSearchTermTop(e);
            }}
            placeholder="Search workflows"
          />
          <StyledWorkflowContainer className={"workflow-container"}>
            {filteredWorkflows.map((workflow) => (
              <Workflow
                key={workflow}
                icon="add"
                workflow={workflow}
                onPress={() => {
                  setSelectedWorkflow(workflow);
                  setIsWorkflowModalOpen(true);
                }}
              />
            ))}
          </StyledWorkflowContainer>
          <NavigationDiv>
            <StyledArrowButton icon={"chevronLeft"} isSmall={true} onPress={scrollLeft} />
            <StyledArrowButton icon={"chevronRight"} isSmall={true} onPress={scrollRight} />
          </NavigationDiv>
          <Modal
            title="Create run"
            isOpen={isWorkflowModalOpen}
            onClose={() => {
              setIsWorkflowModalOpen(false);
            }}
          >
            <Form
              formData={{
                label: "",
                labelSubmitButton: "Create Run",
                isAutoSubmit: false,
                hasChangeIndicator: false,
                input_fields: [
                  {
                    type: "text",
                    name: "runname",
                    label: "With name:",
                    isVisible: true,
                  },
                  {
                    type: "dropdown",
                    name: "workflow",
                    label: "With workflow:",
                    options: workflowOptions,
                    value: selectedWorkflow,
                    isVisible: true,
                  },
                  {
                    type: "dropdown",
                    name: "df_mode",
                    label: "With memory mode:",
                    options: [
                      { label: "disk", value: "disk" }, // TODO change label to "Standard" after backend refactor
                      { label: "disk_memory", value: "disk_memory" }, // TODO change label to "Low Memory" after backend refactor
                    ],
                    isVisible: true,
                  },
                ],
              }}
              onChange={(data) => {
                handleContinueRun(data);
              }}
            ></Form>
          </Modal>
          <Modal
            title="Export a workflow"
            isOpen={isExportModalOpen}
            onClose={() => {
              closeExportModal();
            }}
          >
            {workflows.length > 1 ? (
              <Form
                formData={{
                  label: "",
                  labelSubmitButton: "Export",
                  isAutoSubmit: false,
                  hasChangeIndicator: false,
                  input_fields: [
                    {
                      type: "dropdown",
                      name: "workflow",
                      label: "Workflow:",
                      options: workflows.map((workflow) => ({
                        label: workflow,
                        value: workflow,
                      })),
                      isVisible: true,
                    },
                  ],
                }}
                onChange={(data) => {
                  void handleExportWorkflow(data.workflow);
                }}
              ></Form>
            ) : (
              <SectionTitle baseComponent={"h4"} description={"No workflows available"} />
            )}
          </Modal>
          <Modal
            title="Import a workflow"
            isOpen={isImportModalOpen}
            onClose={() => {
              closeImportModel();
            }}
          >
            <Form
              formData={{
                label: "",
                labelSubmitButton: "Import",
                isAutoSubmit: false,
                hasChangeIndicator: false,
                input_fields: [
                  {
                    type: "file",
                    name: "workflow",
                    label: "Workflow:",
                    isVisible: true,
                  },
                  {
                    type: "text",
                    name: "name",
                    label: "Rename the workflow: (optional)",
                    isVisible: true,
                  },
                ],
              }}
              onChange={(data) => {
                void handleImportWorkflow(data.workflow, data.name);
              }}
            ></Form>
          </Modal>
        </StyledTemplateCard>

        <StyledRunSelectionCard
          title={
            <StyledHeader>
              Run Selection
              <StyledButtonDiv>
                <StyledLeftButton
                  onClick={() => {
                    openExportRunModal();
                  }}
                  icon="download"
                  tooltip="Export a run"
                  tooltipPosition={"bottom"}
                ></StyledLeftButton>
                <StyledRightButton
                  onClick={() => {
                    openImportRunModal();
                  }}
                  icon="download"
                  tooltip="Import a run"
                  tooltipPosition={"bottom"}
                ></StyledRightButton>
              </StyledButtonDiv>
            </StyledHeader>
          }
        >
          <Modal
            title="Run tags:"
            isOpen={isTagModalOpen}
            onClose={() => {
              setIsTagModalOpen(false);
            }}
          >
            <TagMenu
              setSelectedRun={setSelectedRun}
              selectedRun={selectedRun}
              handleAddTag={handleAddTag}
              handleDeleteTag={handleDeleteTag}
            />
          </Modal>
          <Modal
            title="Export a run"
            isOpen={isExportRunModalOpen}
            onClose={() => {
              closeExportRunModal();
            }}
          >
            {runs.length > 1 ? (
              <Form
                formData={{
                  label: "",
                  isAutoSubmit: false,
                  hasChangeIndicator: false,
                  input_fields: [
                    {
                      type: "dropdown",
                      name: "run",
                      label: "Choose a run:",
                      options: runs.map((run) => ({ label: run.run_name, value: run.run_name })),
                      isVisible: true,
                    },
                  ],
                }}
                onChange={(data) => {
                  void handleExportRun(data.run);
                }}
              ></Form>
            ) : (
              <SectionTitle baseComponent={"h4"} description={"No runs available"} />
            )}
          </Modal>
          <Modal
            title="Import a run"
            isOpen={isImportRunModalOpen}
            onClose={() => {
              closeImportRunModal();
            }}
          >
            <Form
              formData={{
                label: "",
                isAutoSubmit: false,
                hasChangeIndicator: false,
                input_fields: [
                  {
                    type: "file",
                    name: "run",
                    label: "Choose a run (.zip):",
                    isVisible: true,
                  },
                ],
              }}
              onChange={(data) => {
                void handleImportRun(data.run);
              }}
            ></Form>
          </Modal>
          <StyledDiv>
            <SearchInputField
              style={{ padding: "0", gap: "0", width: "30%" }}
              value={searchTermRuns}
              onChange={(e) => {
                setSearchTermRuns(e);
              }}
              placeholder="Search runs"
              subscript={"Search by run name, steps, or tags"}
            />
          </StyledDiv>
          <RunsTable
            runs={runs}
            filteredRuns={filteredRuns}
            setRuns={setRuns}
            openTagModal={setIsTagModalOpen}
            setSelectedRun={setSelectedRun}
          />
        </StyledRunSelectionCard>
      </StyledContainer>
    </div>
  );
};
