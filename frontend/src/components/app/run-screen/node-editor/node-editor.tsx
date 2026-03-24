import "@xyflow/react/dist/style.css";
import { useNotification } from "@protzilla/app";
import {
  BackendForm,
  FlexRow,
  GrayButton,
  Icon,
  RedButton,
  SecondaryButton,
} from "@protzilla/core";
import { color, spacing } from "@protzilla/theme";
import type { Step } from "@protzilla/utils";
import {
  callApiWithParameters,
  emptyRunData,
  SectionIDs,
  supportedSections,
} from "@protzilla/utils";
import type { Connection, Edge, EdgeChange, NodeChange, NodeTypes } from "@xyflow/react";
import {
  applyEdgeChanges,
  applyNodeChanges,
  Panel,
  ReactFlow,
  ReactFlowProvider,
  useUpdateNodeInternals,
} from "@xyflow/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { StepSelection } from "../step-selection";
import type { HoveredHandleMeta, StepNodeType } from "./StepNode";
import StepNode from "./StepNode";
import { layoutNodesWithDagre, resolveCollisions } from "./node-editor-layout";
import type { NodeEditorProps } from "./node-editor.props";

const nodeTypes: NodeTypes = { step: StepNode };

const MIN_FLOW_WIDTH = 320;

const StyledRow = styled(FlexRow)`
  gap: ${spacing("verySmall")};
  align-items: flex-start;
  height: 100%;
`;

const StyledFlowColumn = styled.div`
  width: calc(25vw + 24px);
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
`;

const StyledFlowCanvas = styled.div`
  flex: 1;
  min-height: 0;
`;

const StyledDivider = styled.div`
  width: 6px;
  cursor: col-resize;
  position: relative;
  flex: 0 0 6px;
  align-self: stretch;
  margin-right: ${spacing("small")};
  touch-action: none;

  &::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    width: 1px;
    transform: translateX(-50%);
    background-color: ${color("secondary")};
  }
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

const StyledStepButtonsRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${spacing("verySmall")};
  align-items: center;
  margin-bottom: ${spacing("small")};
`;

const NodeInternalsSync: React.FC<{ nodeIds: string[] }> = ({ nodeIds }) => {
  const updateNodeInternals = useUpdateNodeInternals();

  useEffect(() => {
    if (nodeIds.length === 0) return;
    updateNodeInternals(nodeIds);
  }, [nodeIds, updateNodeInternals]);

  return null;
};

export const NodeEditor: React.FC<NodeEditorProps> = ({
  onFormSubmit,
  runName,
  navigateOrRefreshSteps,
  runData,
}) => {
  const notify = useNotification();

  const editorRowRef = useRef<HTMLDivElement>(null);
  const isResizingRef = useRef(false);
  const [flowWidth, setFlowWidth] = useState<number | null>(null);

  //
  // State
  //

  const [nodes, setNodes] = useState<StepNodeType[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const skipNextSyncRef = useRef(false);

  // Mouse-Over info for each handle, displayed in the corner
  const [hoveredHandleMeta, setHoveredHandleMeta] = useState<HoveredHandleMeta>({
    isActive: false,
    direction: "Input",
    type: "protein_df",
  });

  const onAddStep = () => {
    notify({ type: "success", title: "Step added", message: "Successfully added step" });
    navigateOrRefreshSteps();
  };

  const resolveAndPersistNodes = useCallback(
    (nodesToResolve: StepNodeType[], refreshAfter = false) => {
      const resolvedNodes = resolveCollisions(nodesToResolve);
      setNodes(resolvedNodes);

      void Promise.all(
        resolvedNodes.map((node) =>
          callApiWithParameters("set_step_pos/", {
            run_name: runName,
            step_id: node.id,
            x: node.position.x,
            y: node.position.y,
          }),
        ),
      ).then(() => {
        if (refreshAfter) {
          navigateOrRefreshSteps();
        }
      });
    },
    [navigateOrRefreshSteps, runName],
  );

  const nodeIds = useMemo(() => nodes.map((node) => node.id), [nodes]);

  //
  // Data syncing
  //

  useEffect(() => {
    if (runData === emptyRunData) return;

    const syncNodes = runData.displayed_steps.map((step: Step) => ({
      id: step.id,
      type: "step",
      position: step.visual_data?.node_position ?? { x: 0, y: 0 },
      data: {
        step: step,
        section: step.section,
        isSelected: runData.current_step_id === step.id,
        navigateOrRefreshSteps,
        setHoveredHandleMeta,
      },
    })) as StepNodeType[];

    const mergedNodes = syncNodes.map((syncNode) => {
      const existingNode = nodes.find((currentNode) => currentNode.id === syncNode.id);

      if (!existingNode) {
        return syncNode;
      }

      return {
        ...existingNode,
        position: syncNode.position,
        data: syncNode.data,
      };
    });

    const syncEdges = runData.graph_edges;

    setTimeout(() => {
      setEdges(syncEdges);
    }, 0);

    if (syncNodes.length > nodes.length) {
      skipNextSyncRef.current = true;
      resolveAndPersistNodes(mergedNodes);
      return;
    }

    if (skipNextSyncRef.current) {
      skipNextSyncRef.current = false;
      return;
    }

    setNodes(mergedNodes);
  }, [navigateOrRefreshSteps, nodes.length, resolveAndPersistNodes, runData]);

  //
  // Handlers
  //

  const onNodesChange = useCallback((changes: NodeChange<StepNodeType>[]) => {
    setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot));
  }, []);

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot));
  }, []);

  const onEdgeClick = useCallback((_event: React.MouseEvent, edge: Edge) => {
    setSelectedEdge(edge);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedEdge(null);
  }, []);

  const onNodeDragStop = useCallback(
    (_event: unknown, node: StepNodeType) => {
      const draggedNodes = nodes.map((currentNode) =>
        currentNode.id === node.id ? { ...currentNode, ...node } : currentNode,
      );
      resolveAndPersistNodes(draggedNodes, true);
    },
    [nodes, resolveAndPersistNodes],
  );

  const onConnect = useCallback(
    (params: Connection) => {
      void callApiWithParameters("connect_steps/", {
        run_name: runName,
        connection: params,
      }).then((response) => {
        notify({
          type: response.success ? "success" : "error",
          title: response.message.title,
          message: response.message.msg,
        });
        navigateOrRefreshSteps();
      });
    },
    [navigateOrRefreshSteps, notify, runName],
  );

  const onDividerPointerDown = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    isResizingRef.current = true;
    event.currentTarget.setPointerCapture(event.pointerId);
    event.preventDefault();
  }, []);

  const onDividerPointerMove = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    if (!isResizingRef.current || !editorRowRef.current) return;
    const rowRect = editorRowRef.current.getBoundingClientRect();
    const nextWidth = Math.max(event.clientX - rowRect.left, MIN_FLOW_WIDTH);
    setFlowWidth(nextWidth);
  }, []);

  const onDividerPointerUp = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    if (!isResizingRef.current) return;
    isResizingRef.current = false;
    event.currentTarget.releasePointerCapture(event.pointerId);
  }, []);

  const removeCurrentConnection = useCallback(() => {
    if (!selectedEdge) return;
    void callApiWithParameters("disconnect_steps/", {
      run_name: runName,
      connection: {
        source: selectedEdge.source,
        sourceHandle: selectedEdge.sourceHandle,
        target: selectedEdge.target,
        targetHandle: selectedEdge.targetHandle,
      },
    }).then((response) => {
      notify({
        type: response.success ? "success" : "error",
        title: response.message.title,
        message: response.message.msg,
      });
      setSelectedEdge(null);
      navigateOrRefreshSteps();
    });
  }, [navigateOrRefreshSteps, notify, runName, selectedEdge]);

  const onAutoLayout = useCallback(() => {
    const layoutedNodes = layoutNodesWithDagre(nodes, edges);
    setNodes(layoutedNodes);

    Promise.all(
      layoutedNodes.map((node) =>
        callApiWithParameters("set_step_pos/", {
          run_name: runName,
          step_id: node.id,
          x: node.position.x,
          y: node.position.y,
        }),
      ),
    )
      .then(() => {
        notify({ type: "success", title: "Layout updated", message: "Node positions saved" });
        navigateOrRefreshSteps();
      })
      .catch(() => {
        notify({ type: "error", title: "Layout failed", message: "Could not save positions" });
      });
  }, [edges, navigateOrRefreshSteps, nodes, notify, runName]);

  const deleteCurrentStep = async () => {
    await callApiWithParameters("delete_step/", {
      run_name: runName,
      step_id: runData.current_step_id,
    }).then((response) => {
      notify({
        type: response.success ? "success" : "error",
        title: response.message,
      });
      navigateOrRefreshSteps();
    });
  };

  //
  // Derived view state
  //

  const currentStep = useMemo(
    () => runData.displayed_steps.find((s) => s.id === runData.current_step_id),
    [runData],
  );

  // Fallback
  if (runData === emptyRunData || !currentStep) {
    return <h1>Loading editor...</h1>;
  }

  const buttonText =
    currentStep.status === "complete"
      ? "Next"
      : (runData.current_section as SectionIDs) === SectionIDs.Importing
        ? "Import"
        : "Calculate";

  const stepSelectionProps = {
    runName: runName,
    onAddStep: onAddStep,
  };

  return (
    <StyledRow ref={editorRowRef}>
      <StyledFlowColumn style={flowWidth ? { width: flowWidth } : undefined}>
        <StyledStepButtonsRow>
          {supportedSections.map((section) => (
            <StepSelection
              key={`add-button-for-section-${section.id as string}`}
              section={section.id}
              ModalTrigger={(openModal) => (
                <>
                  <SecondaryButton onClick={openModal}>
                    <Icon icon={section.id} style={{ flexShrink: 0, marginRight: "10px" }} /> Add{" "}
                    {section.name}
                  </SecondaryButton>
                </>
              )}
              {...stepSelectionProps}
            />
          ))}
        </StyledStepButtonsRow>

        <StyledFlowCanvas>
          <ReactFlowProvider>
            <ReactFlow
              key={runName}
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onEdgeClick={onEdgeClick}
              onPaneClick={onPaneClick}
              onNodeDragStop={onNodeDragStop}
              onConnect={onConnect}
              fitView
            >
              <NodeInternalsSync nodeIds={nodeIds} />
              <Panel position="top-left">
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  <GrayButton onClick={onAutoLayout}>Tidy layout</GrayButton>
                  <RedButton onClick={() => void deleteCurrentStep()}>
                    Remove current step
                  </RedButton>
                  {selectedEdge && (
                    <RedButton onClick={removeCurrentConnection} isDisabled={!selectedEdge}>
                      Remove selected connection
                    </RedButton>
                  )}
                </div>
              </Panel>

              <Panel position="top-right">
                {hoveredHandleMeta.isActive && (
                  <div
                    style={{
                      textAlign: "right",
                      backgroundColor: "white",
                      padding: "10px",
                      border: "2px solid black",
                    }}
                  >
                    <p>{hoveredHandleMeta.direction}</p>
                    <p>{hoveredHandleMeta.type}</p>
                  </div>
                )}
              </Panel>
            </ReactFlow>
          </ReactFlowProvider>
        </StyledFlowCanvas>
      </StyledFlowColumn>

      <StyledDivider
        onPointerDown={onDividerPointerDown}
        onPointerMove={onDividerPointerMove}
        onPointerUp={onDividerPointerUp}
        onPointerCancel={onDividerPointerUp}
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize node editor"
      />

      <StyledFormColumn>
        <BackendForm
          runName={runName}
          buttonText={buttonText}
          previousStepCalculationStatus={"complete"}
          currentStepCalculationStatus={currentStep.status}
          current_step_id={runData.current_step_id}
          isLastStep={!runData.recommended_next_step_id}
          onNext={() => {
            navigateOrRefreshSteps(runData.recommended_next_step_id);
          }}
          onSubmit={onFormSubmit}
          onChange={() => {
            navigateOrRefreshSteps();
          }}
          runData={runData}
        />
      </StyledFormColumn>
    </StyledRow>
  );
};
