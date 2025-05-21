import React, { useCallback, useEffect, useState } from "react";
import { Container } from "react-grid-system";
import { useNavigate } from "react-router-dom";
import { styled, useTheme } from "styled-components";
import "bootstrap/dist/css/bootstrap.min.css";

import {
  Card,
  Form,
  Icon,
  InputValueType,
  Modal,
  Navbar,
  RunsTable,
  SecondaryButton,
  Tooltip,
  useNotification,
  useTooltipScheduling,
  Workflow,
} from "../components";
import { SearchInputField } from "../components/input-fields/search-input-field";
import { TagMenu } from "../components/taglist/tag-menu.tsx";
import { size, spacing, styledDiv } from "../theme";
import { callApi, callApiWithParameters, Run } from "../utils";

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
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
  padding: ${spacing("small")};
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

const InfoIcon = styled(Icon)`
  padding-left: 10px;
`;

export const IndexScreen: React.FC = () => {
  const navigate = useNavigate();
  const notify = useNotification();
  const theme = useTheme();

  const { handlePointerEnter, handlePointerLeave, showTooltip, mouseAnchor } =
    useTooltipScheduling(true);
  const [, setParentRef] = useState<HTMLDivElement | null>(null);

  const [workflows, setWorkflows] = useState<string[]>([]);
  const [searchTermTop, setSearchTermTop] = useState<string>("");
  const [searchTermRuns, setSearchTermRuns] = useState<string>("");
  const [isWorkflowModalOpen, setIsWorkflowModalOpen] = useState(false);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);
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

  const workflowContainerSize = parseInt(
    (theme.sizes.bigButtonContainerDimension as unknown as string).replace("px", ""),
  );

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
        allowRunEdit={false}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => void navigate("/")}
      />

      <StyledContainer>
        <StyledTemplateCard title="Template Workflows">
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
