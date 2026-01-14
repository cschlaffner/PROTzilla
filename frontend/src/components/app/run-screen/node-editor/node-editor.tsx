import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';

import { useState, useEffect, useCallback } from 'react';
import { ReactFlow, applyNodeChanges, applyEdgeChanges, addEdge, Panel } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import StepNode from "./StepNode.tsx";
import { BackendForm, FlexRow, SecondaryButton, RedButton} from "@protzilla/core";
import { styled } from "styled-components";
import { color, spacing } from "@protzilla/theme";
 
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
 
  const onNodesChange = useCallback(
    (changes) => setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
    [],
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
    [],
  );
  const onConnect = useCallback(
    (params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
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

  useEffect(() => {
    console.log(runData);
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
 
  return (
    <StyledRow>
    <div style={{ width: '25vw', height: '100vh' }}>
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
        <SecondaryButton onClick={undefined}>
          Add step
        </SecondaryButton>
        <RedButton onClick={undefined}>
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
