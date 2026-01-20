import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';

import { useState, useEffect, useCallback } from 'react';
import { ReactFlow, applyNodeChanges, applyEdgeChanges, addEdge, Panel } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import StepNode from "./StepNode.tsx";
import { BackendForm, FlexRow, SecondaryButton, RedButton} from "@protzilla/core";
import { styled } from "styled-components";
import { color, spacing } from "@protzilla/theme";
import { useNotification } from "@protzilla/app";
import { callApiWithParameters, translateGlobalToSectionIndex } from "@protzilla/utils";
import { StepSelection } from "../step-selection";
import { Icon } from "@protzilla/core";
 
const initialNodes = [];

const initialEdges = [{ id: 'n1-n1', source: 'n1', target: 'n1' }];
const nodeTypes = {step: StepNode};

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
  width: 20vw;
  min-width: 250px;
  max-width: 500px;
  height: 100%;
  overflow-y: auto;
  overflow-x: auto;
  min-height: 0;
  gap: ${spacing("large")};
  padding-top: ${spacing("small")};
  padding-bottom: ${spacing("medium")};
  padding-right: ${spacing("medium")};
  margin: 0 ${spacing("small")};
`;


export const NodeEditor: React.FC<NodeEditorProps> = ({
  onFormSubmit,
  runName,
  navigateOrRefreshSteps,
  runData,
}) => {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
 
  // TODO: When do we want to propagate positions to the backend?
  // This function gets called wayy to frequently to use for that.
  // Maybe on every new step selection?
  const onNodesChange = useCallback(
    (changes) => {
      setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot));
    },
    [],
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
    [],
  );

  const getEdgesFromRunData = () => {
    // TODO: This needs to be implemented when the API provides sufficient data.
    return initialEdges;
  }

  // TODO: Implement this in API
  const connectSteps = async (params) => {
    await callApiWithParameters("connect_steps/", {
      run_name: runName,
      connection: params
    }).then((response) => {
      notify({
        type: response.success ? "success" : "error",
        title: response.message,
      });
    });
    navigateOrRefreshSteps();
  };

  const onConnect = useCallback(
    (params) => {
      // connectSteps(params);
      // setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot));
      setEdges(getEdgesFromRunData());
    },
    [],
  );

  const sections = runData.displayed_steps;

  const currentSection = sections.find(
    (section) => (section.id as string) === runData.current_section,
  );

  const currentStepCalculationStatus = currentSection?.steps[runData.current_step_index]?.status;
  const buttonText =
    currentStepCalculationStatus === "complete"
      ? "Next"
      : runData.current_section === "importing"
        ? "Import"
        : "Calculate";

  const [hoveredHandleMeta, setHoveredHandleMeta] = useState({
    "isActive": false,
    "direction": "Input", 
    "type": "protein_df"
  });

  const notify = useNotification();
  const deleteCurrentStep = async () => {
    await callApiWithParameters("delete_step/", {
      run_name: runName,
      section: runData.current_section,
      index: translateGlobalToSectionIndex(runData.current_step_index, sections).index,
    }).then((response) => {
      notify({
        type: response.success ? "success" : "error",
        title: response.message,
      });
    });
    navigateOrRefreshSteps();
  };

  useEffect(() => {
    console.log("Run Data", runData);
    let new_nodes = [];
    let y_offset = 0;
    let flat_step_index = 0;

    runData.displayed_steps.forEach(section => {
      section.steps.forEach((step, index) => {
          
        const isSelected = 
          (runData.current_section === section.id) && 
          (runData.current_step_index === flat_step_index);

        // Retain positions on redraw
        const old_matching_node = nodes.find((node) => node.id == step.id);
        const position = old_matching_node
          ? old_matching_node.position
          : {x: 0, y: y_offset}
       
        new_nodes.push({
          id: step.id, 
          type: "step", 
          position: position,
          data: {
            step: step, 
            step_index_within_section: index,
            section: section.id,
            isSelected: isSelected,
            navigateOrRefreshSteps: navigateOrRefreshSteps,
            setHoveredHandleMeta: setHoveredHandleMeta
          }
        });

        flat_step_index += 1;
        y_offset += 60;
      });
    });
    setNodes(new_nodes);
  }, [runData])

  const onAddStep = () => {
    notify({"type": "success", "message": "haha yes."});
    navigateOrRefreshSteps();
  }

  const step_selection_props = {
    runName: runName,
    index: 0, 
    onAddStep: onAddStep,
  }
 
  return (
    <StyledRow>
    <div style={{ width: '25vw', height: '100vh' }}>
        {
          sections.map((section) => 
        <StepSelection
          section={section.id}
          ModalTrigger={(openModal) => (
            <>
            <SecondaryButton onClick={openModal}>
            <Icon icon={section.id} style={{ flexShrink: 0, marginRight: "10px" }} /> Add {section.name}
            </SecondaryButton>
            </>
          )}
          {... step_selection_props}
        />
                      )
        }

        <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        >
      
      <Panel position="top-left">
        <RedButton onClick={deleteCurrentStep}>
          Remove current step
        </RedButton>

      </Panel>

      <Panel position="top-right">
      { hoveredHandleMeta["isActive"] && (
        <div style={{textAlign: "right"}}>
          <p>{hoveredHandleMeta["direction"]}</p>
          <p>{hoveredHandleMeta["type"]}</p>
        </div>
      )}
      </Panel>
      </ReactFlow>
    </div>

    <StyledDivider />

    {/* TODO: Well, this is stupid. We probably need to redefine this component.
      previousStepCalculationStatus does not make a lot of sense with the new system.
      onNext also isn't really a thing anymore I suppose.
      onChange suffers from similar problems, but should be doable.
      Gotta discuss this in a meeting
    */}
    <StyledFormColumn>
      <BackendForm
        runName={runName}
        buttonText={buttonText}
        previousStepCalculationStatus={"complete"}
        currentStepCalculationStatus={currentStepCalculationStatus}
        current_step_index={runData.current_step_index}
        isLastStep={
          runData.current_step_index >=
          runData.displayed_steps
            .map((section) => section.steps.length)
            .reduce((acc, val) => acc + val, 0) -
            1
        }
        onNext={() => console.log("TODO: A vulture ate this callback! Come up with something better.")}
        onSubmit={onFormSubmit}
        onChange={() => console.log("TODO: A vulture ate this callback! Come up with something better.")}
      />
    </StyledFormColumn>
    </StyledRow>
  );
}
