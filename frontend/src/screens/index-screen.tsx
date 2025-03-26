import React, { useEffect, useState} from "react";
import { Container } from "react-grid-system";
import { styled } from "styled-components";
import { Navbar } from "../components/navbar";
import { useNavigate } from "react-router-dom";
import { Card, Form, Modal, RunsTable, Workflow } from "../components";
import { size, spacing } from "../theme";
import { callApi, Run } from "../utils";

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
  const [runs, setRuns] = useState<Run[]>({} as Run[]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await callApi("run_information/");
      if (data) {
        setRuns(data);
      }
    };

    void fetchData();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const data = await callApi("workflow_name_list/");
      if (data) {
        console.log(data);
        setWorkflows(data);
        }
      }

    void fetchData();
  }, []);


  return (
    <div>
      <StyledNavbar
        allowRunEdit={false}
        onNavigateHome={() => navigate("/")}
        onOpenSettings={() => {}}
        onOpenHelp={() => {}}
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
                name: "workflow-drop",
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
          onChange={ () => {}}></Form>
          </Test>
        </Modal>
      </StyledTemplateCard>

        <StyledRunSelectionCard title="Run Selection">
          <Modal title="Run tags:" isOpen={isTagModalOpen} onClose={() => { setIsTagModalOpen(false); }}>bing</Modal>
          <RunsTable runs={runs} setRuns={setRuns}/>
        </StyledRunSelectionCard>
      </StyledContainer>
    </div>
  );
};
