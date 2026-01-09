import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';

import { useState, useEffect, useCallback } from 'react';
import { ReactFlow, applyNodeChanges, applyEdgeChanges, addEdge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import StepNode from "./StepNode.tsx";
 
const initialNodes = [];

const initialEdges = [{ id: 'n1-n1', source: 'n1', target: 'n1' }];
const nodeTypes = {step: StepNode};



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

  useEffect(() => {
    console.log(runData);
    let new_nodes = [];
    let y_offset = 0;

    runData.displayed_steps.forEach(section => {
      section.steps.forEach((step, index) => {
        new_nodes.push({
          id: step.id, 
          type: "step", 
          position: {x: 0, y: y_offset}, 
          data: {
            step: step, 
            step_index_within_section: index,
            section: section.id,
            navigateOrRefreshSteps: navigateOrRefreshSteps,
          }
        });

        y_offset += 40;
      });
    });
    setNodes(new_nodes);
  }, [runData])
 
  return (
    <div style={{ width: '25vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      />
    </div>
  );
}
