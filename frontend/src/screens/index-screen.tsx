import React, { useEffect, useState} from "react";
import { Container } from "react-grid-system";
import { useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { Card, Form, Icon, Modal, RunsTable, Workflow } from "../components";
import { Navbar } from "../components/navbar";
import { color, size, spacing } from "../theme";
import { callApi, callApiWithParameters, Run } from "../utils";


//this will be a tag component, do before merge
const TagList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`
//this will be a tag component, do before merge
const Tag = styled.span`
  background-color: ${color("protzillaDarkBlue")};
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
`

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const Test = styled.div`
`;

const StyledContainer = styled(Container)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-direction: column;
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
`;

const StyledRunSelectionCard = styled(Card)`
  height: calc(
    100vh -
      (
        ${spacing("navbarHeight")} + 7 * ${spacing("small")} +
          ${size("templateSelectionHeight")}
      )
  );
  min-height: ${size("runSelectionMinHeight")};
`;

export const IndexScreen: React.FC = () => {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState([]);
  const [isWorkflowModalOpen, setIsWorkflowModalOpen] = useState(false);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState("");
  const [runs, setRuns] = useState<Run[]>([] as Run[]);
  const [selectedRun, setSelectedRun] = useState<Run>(() => ({          //lazy initialization to prevent .map() error
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
      const data = await callApi("run_information/");
      if (data) {
        setRuns(data[0]);
      }
    };

    void fetchData();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const data = await callApi("workflow_name_list/");
      if (data) {
        setWorkflows(data);
        }
      }

    void fetchData();
  }, []);

  const handleAddTag = (tag: string) => {
    void callApiWithParameters("add_tag/", {
      run_name: selectedRun.run_name,
      tag_name: tag,
    });
    const updated = runs.map((run) =>
      run.run_name === selectedRun.run_name ? { ...run, run_tags: [...run.run_tags, tag] } : run
    );
    setRuns(updated);
    setSelectedRun((run) => ({ ...run, run_tags: [...run.run_tags, tag] }));
  }
  //grrr code duplikation grrrr
  const handleDeleteTag = (runName: string, tagToDelete: string) => {
    void callApiWithParameters("delete_tag/", {
      run_name: runName,
      tag_name: tagToDelete,
    });
    setRuns((runs) =>
      runs.map((run) =>
        run.run_name === runName
          ? { ...run, run_tags: run.run_tags.filter((tag) => tag !== tagToDelete) }
          : run
      )
    );
    setSelectedRun((run) => 
      ({ ...run, run_tags: run.run_tags.filter((tag) => tag !== tagToDelete) })
    );
  };

  return (
    <div>
      <StyledNavbar
        allowRunEdit={false}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => void navigate("/")}
      />

      <StyledContainer fluid>
      <StyledTemplateCard title="Template Workflows">
        <StyledWorkflowContainer >
          {workflows.map((workflow) => (
            <Workflow
              key={workflow}
              icon="add"
              workflow={workflow}
              onPress={() => { 
                setSelectedWorkflow(workflow);
                setIsWorkflowModalOpen(true); }}
            />
          ))}
        </StyledWorkflowContainer>
        <Modal title="Create run:" isOpen={isWorkflowModalOpen} onClose={() => { setIsWorkflowModalOpen(false); }}>
          <Test>
          <Form formData={{
            label: "",
            isAutoSubmit: false,
            input_fields: [
              {
                type: "text",
                name: "runname",
                props: {
                  label: "With name:",
                },
              },
              {
                type: "dropdown",
                name: "workflow",
                props: {
                  label: "With workflow:",
                  options: [
                    { label: selectedWorkflow, value: selectedWorkflow },
                  ],
                },
              },
              {
                type: "dropdown",
                name: "df_mode",
                props: {
                  label: "With memory mode:",
                  options: [
                    { label: "Standard", value: "disk" },
                    { label: "Low Memory", value: "disk_memory" },
                  ],
                },
              },
            ],
          }} 
          onChange={ (data) => { void callApiWithParameters("add_run/", {
                run_name: data.runname ?? "",
                workflow_name: data.workflow ?? "",
                df_mode_name: data.df_mode ?? "disk",
              })}}></Form>
          </Test>
        </Modal>
      </StyledTemplateCard>

        <StyledRunSelectionCard title="Run Selection">
          <Modal title="Run tags:" isOpen={isTagModalOpen} onClose={() => { setIsTagModalOpen(false); }}>
          <TagList>
            {selectedRun.run_tags.map((tag, i) => (
              <Tag key={i}>
                {tag}
                <Icon 
                  icon="close"
                  color="gray"
                  onClick={() => { handleDeleteTag(selectedRun.run_name, tag); }}
                  aria-label={`Remove tag ${tag}`}
                  style={{
                  height: "15px",
                  }}
                />
              </Tag>
            ))}
            </TagList>
          <Form formData={{
            label: "",
            isAutoSubmit: false,
            input_fields: [
              {
                type: "text",
                name: "tag",
                props: {
                  label: "Add a new tag:",
                },
              },
            ],
          }} 
          onChange={ (data) => {handleAddTag(data.tag as string) }}></Form>
          </Modal>
          <RunsTable runs={runs} setRuns={setRuns} openModal={setIsTagModalOpen} setSelectedRun={setSelectedRun}/>
        </StyledRunSelectionCard>
      </StyledContainer>
    </div>
  );
};
