import React, { useEffect, useState} from "react";
import { Container } from "react-grid-system";
import { useNavigate } from "react-router-dom";
import { styled } from "styled-components";

import { Card, Form, Modal, RunsTable, Workflow } from "../components";
import { SearchInputField } from "../components/input-fields/search-input-field";
import { Navbar } from "../components/navbar";
import { TagList } from "../components/taglist";
import { size, spacing } from "../theme";
import { callApi, callApiWithParameters, Run } from "../utils";

const StyledModalChild = styled.div`
  padding: ${spacing("small")};
`;

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
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
  const [workflows, setWorkflows] = useState<string[]>([]);
  const [searchTermTags, setSearchTermTags] = useState<string>("");
  const [searchTermTop, setSearchTermTop] = useState<string>("");
  const [searchTermRuns, setSearchTermRuns] = useState<string>("");
  const [isWorkflowModalOpen, setIsWorkflowModalOpen] = useState(false);
  const [isTagModalOpen, setIsTagModalOpen] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState("");
  const [runs, setRuns] = useState<Run[]>([] as Run[]);
  const [existingTags, setExistingTags] = useState<string[]>([]);
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
      const data = await callApi("run_information/");
      if (data) {
        setRuns(data[0]);
        setExistingTags(data[1]);
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

  const filteredWorkflows = workflows.filter((workflow) =>
    workflow.toLowerCase().includes(searchTermTop.toLowerCase()),
  );

  const filteredRuns = runs.filter((run) =>
    run.run_name.toLowerCase().includes(searchTermRuns.toLowerCase()) ||
    run.modification_date.toLowerCase().includes(searchTermRuns.toLowerCase()) ||
    run.run_tags.some(tag => tag.toLowerCase().includes(searchTermRuns.toLowerCase())) ||
    run.run_steps.some(step => step.toLowerCase().includes(searchTermRuns.toLowerCase())),
  );

  const addableTags = existingTags.filter((tag) => !selectedRun.run_tags.includes(tag));
  const filteredAddableTags = addableTags.filter((tag) =>
    tag.toLocaleLowerCase().includes(searchTermTags.toLocaleLowerCase()),
  );

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
    setExistingTags((tags) => tags.includes(tag) ? tags : [...tags, tag]);
  }

  const handleDeleteTag = (tagToDelete: string) => {
    void callApiWithParameters("delete_tag/", {
      run_name: selectedRun.run_name,
      tag_name: tagToDelete,
    });
    setRuns((runs) =>
      runs.map((run) =>
        run.run_name === selectedRun.run_name
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
        <SearchInputField
                    style={{ padding: "0", gap: "0", width: "30%"}}
                    value={searchTermTop}
                    onChange={(e) => {
                      setSearchTermTop(e);
                    }}
                    placeholder="Search workflows"
                    smallBorder={true}
                    isSmall={true}
                  />
        <StyledWorkflowContainer >
          {filteredWorkflows.map((workflow) => (
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
          <Form formData={{
            label: "",
            isAutoSubmit: false,
            hasChangeIndicator: false,
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
        </Modal>
      </StyledTemplateCard>

        <StyledRunSelectionCard title="Run Selection">
          <Modal title="Run tags:" isOpen={isTagModalOpen} onClose={() => { setIsTagModalOpen(false); }}>
            <TagList runName={selectedRun.run_name} tags={selectedRun.run_tags} icon="close" handleTag={handleDeleteTag}/>
            <Form formData={{
              label: "",
              isAutoSubmit: false,
              hasChangeIndicator: false,
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
            <SearchInputField
              label="Or choose from existing tags:"
              style={{ padding: "0", gap: "0"}}
              value={searchTermTags}
              onChange={(e) => {
                setSearchTermTags(e);
              }}
              placeholder="Search existing tags"
              smallBorder={true}
              isSmall={true}
            />
            <StyledModalChild>
              <TagList runName={selectedRun.run_name} tags={filteredAddableTags} icon="add" handleTag={handleAddTag}/>
            </StyledModalChild>
          </Modal>
          <SearchInputField
            style={{ padding: "0", gap: "0", width: "30%"}}
            value={searchTermRuns}
            onChange={(e) => {
              setSearchTermRuns(e);
            }}
            placeholder="Search runs"
            smallBorder={true}
            isSmall={true}
          />
          <RunsTable 
            runs={runs} 
            filteredRuns={filteredRuns} 
            setRuns={setRuns} 
            openModal={setIsTagModalOpen} 
            setSelectedRun={setSelectedRun}
          />
        </StyledRunSelectionCard>
      </StyledContainer>
    </div>
  );
};
