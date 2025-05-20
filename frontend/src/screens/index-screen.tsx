import React, { useCallback, useEffect, useState } from "react";
import { Container } from "react-grid-system";
import { useNavigate } from "react-router-dom";
import { styled } from "styled-components";
import "bootstrap/dist/css/bootstrap.min.css";

import {
  Button,
  Card,
  Form,
  Icon,
  InputValueType,
  Modal,
  Navbar,
  RunsTable,
  SectionTitle,
  Tooltip,
  useNotification,
  useTooltipScheduling,
  Workflow,
} from "../components";
import { SearchInputField } from "../components/input-fields/search-input-field";
import { TagMenu } from "../components/taglist/tag-menu.tsx";
import { size, spacing, styledDiv } from "../theme";
import { callApi, callApiWithParameters, Run } from "../utils";
import { saveAs } from "file-saver";

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const StyledContainer = styled.div`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
`;

const StyledWorkflowContainer = styled(Container)`
  display: flex;
  overflow-x: hidden;

  scrollbar-width: thin;
  scrollbar-color: #888 transparent;

  &::-webkit-scrollbar {
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }
  &:hover {
    overflow-x: auto;
  }
`;

const StyledTemplateCard = styled(Card)`
  height: ${size("templateSelectionHeight")};
  width: calc(100vw - (2 * ${spacing("small")}));
`;

const StyledRunSelectionCard = styled(Card)`
  min-height: ${size("runSelectionMinHeight")};
  height: calc(
    100vh - ${spacing("navbarHeight")} - ${size("templateSelectionHeight")} -
      (5 * ${spacing("small")})
  );
  width: calc(100vw - (2 * ${spacing("small")}));
  box-sizing: border-box;

  overflow-y: auto;
`;

const StyledDiv = styledDiv.div`
  display: flex;
  flex-direction: row;
`;

const InfoIcon = styled(Icon)`
  padding-left: 10px;
`;

export const IndexScreen: React.FC = () => {
  const navigate = useNavigate();
  const notify = useNotification();

  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(true);
  const [, setParentRef] = useState<HTMLDivElement | null>(null);

  const [workflows, setWorkflows] = useState<string[]>([]);
  const [searchTermTop, setSearchTermTop] = useState<string>("");
  const [searchTermRuns, setSearchTermRuns] = useState<string>("");
  const [isWorkflowModalOpen, setIsWorkflowModalOpen] = useState(false);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
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

  useEffect(() => {
    const fetchData = async () => {
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

    void fetchData();
  }, [notify]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await callApi("workflow_name_list/");
      if (data) {
        setWorkflows(data);
      }
    };

    void fetchData();
  }, []);

  const filteredWorkflows = workflows.filter((workflow) =>
    workflow.toLowerCase().includes(searchTermTop.toLowerCase()),
  );

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

  const handleExportWorkflow = async (workflowName: InputValueType) => {
    const blob: Blob = await callApiWithParameters(
      "export_workflow/",
      { workflow_name: workflowName ?? "standard" },
      "blob",
    );
    saveAs(blob, workflowName + ".yaml");
  };

  return (
    <div>
      <StyledNavbar
        allowRunEdit={false}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => void navigate("/")}
      />

      <StyledContainer>
        <StyledTemplateCard
          title={
            //these two divs will be replaced by named styled divs defined above with the rest fo styled componetns
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                width: "100%",
              }}
            >
              Template Workflows
              <div style={{ display: "flex", gap: "10px" }}>
                <Button
                  onClick={() => setIsExportModalOpen(true)}
                  icon="download"
                  tooltip="Export a workflow"
                  tooltipPosition={"bottom"}
                ></Button>
                <Button
                  onClick={() => setIsImportModalOpen(true)}
                  icon="upload"
                  tooltip="Import a workflow"
                  tooltipPosition={"bottom"}
                ></Button>
              </div>
            </div>
          }
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <SearchInputField
              style={{ padding: "0", gap: "0", width: "30%" }}
              value={searchTermTop}
              onChange={(e) => {
                setSearchTermTop(e);
              }}
              placeholder="Search workflows"
            />
            <Button
              onClick={() => setIsExportModalOpen(true)}
              icon="download"
              tooltip="Export a workflow"
              tooltipPosition={"bottom"}
            ></Button>
          </div>
          <StyledWorkflowContainer>
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
                    options: [{ label: selectedWorkflow, value: selectedWorkflow }],
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
              setIsExportModalOpen(false);
            }}
          >
            {" "}
            {workflows.length > 1 ? (
              <Form
                formData={{
                  label: "",
                  isAutoSubmit: false,
                  hasChangeIndicator: false,
                  input_fields: [
                    {
                      type: "dropdown",
                      name: "workflow",
                      label: "workflow:",
                      options: workflows.map((workflow) => ({ label: workflow, value: workflow })),
                      isVisible: true,
                    },
                  ],
                }}
                onChange={(data) => {
                  handleExportWorkflow(data.workflow);
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
              setIsImportModalOpen(false);
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
                    name: "workflow",
                    label: "workflow:",
                    isVisible: true,
                  },
                ],
              }}
              onChange={(data) => {
                void callApiWithParameters("import_workflow/", {
                  workflow_file: data.workflow ?? "",
                });
              }}
            ></Form>
          </Modal>
        </StyledTemplateCard>

        <StyledRunSelectionCard title="Run Selection">
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
          <StyledDiv>
            <SearchInputField
              style={{ padding: "0", gap: "0", width: "30%" }}
              value={searchTermRuns}
              onChange={(e) => {
                setSearchTermRuns(e);
              }}
              placeholder="Search runs"
            />
            <div
              onPointerEnter={handlePointerEnter}
              onPointerLeave={handlePointerLeave}
              ref={setParentRef}
            >
              <InfoIcon icon={"info"} isSmall={true} style={{ paddingLeft: "10px" }} />
              <Tooltip
                text={"Search by run name, steps, or tags"}
                isShown={showTooltip}
                anchor={mouseAnchor}
                distance={5}
                position={"bottomRight"}
              />
            </div>
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
