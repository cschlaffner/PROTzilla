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
import { applyEdgeChanges, applyNodeChanges, Panel, ReactFlow } from "@xyflow/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { styled } from "styled-components";

import { StepSelection } from "../step-selection";
import type { HoveredHandleMeta, StepNodeType } from "./StepNode";
import StepNode from "./StepNode";
import { layoutNodesWithDagre } from "./node-editor-layout";
import { NodeEditorProps } from "./node-editor.props";

const nodeTypes: NodeTypes = { step: StepNode };

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

const StyledStepButtonsRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${spacing("verySmall")};
  align-items: center;
  margin-bottom: ${spacing("small")};
`;

export const NodeEditor: React.FC<NodeEditorProps> = ({
  onFormSubmit,
  runName,
  navigateOrRefreshSteps,
  runData,
}) => {
  const notify = useNotification();

  //
  // State
  //

  const [nodes, setNodes] = useState<StepNodeType[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const dragStartPositionsRef = useRef<Record<string, { x: number; y: number } | undefined>>({});

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
    }));

    setNodes(syncNodes as StepNodeType[]);
  }, [runData, navigateOrRefreshSteps]);

  const fetchEdges = useCallback(async () => {
    try {
      const res = await callApiWithParameters("get_edges/", { run_name: runName });
      if (res.data) setEdges(res.data as Edge[]);
    } catch (err) {
      console.error("Failed to fetch edges", err);
    }
  }, [runName]);

  useEffect(() => {
    void fetchEdges();
  }, [fetchEdges, runData.current_step_id]); // Refresh edges when step changes

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

  const getNodeRect = useCallback((node: StepNodeType) => {
    const width = node.width ?? 260;
    const height = node.height ?? 72;
    return {
      x: node.position.x,
      y: node.position.y,
      width,
      height,
    };
  }, []);

  const nodesOverlap = useCallback(
    (node: StepNodeType, other: StepNodeType) => {
      const a = getNodeRect(node);
      const b = getNodeRect(other);
      return (
        a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y
      );
    },
    [getNodeRect],
  );

  const onNodeDragStart = useCallback((_event: unknown, node: StepNodeType) => {
    dragStartPositionsRef.current[node.id] = { x: node.position.x, y: node.position.y };
  }, []);

  const onNodeDragStop = useCallback(
    (_event: unknown, node: StepNodeType) => {
      const isOverlapping = nodes.some(
        (other) => other.id !== node.id && nodesOverlap(node, other),
      );
      if (isOverlapping) {
        const originalPosition = dragStartPositionsRef.current[node.id];
        if (originalPosition) {
          setNodes((prev) =>
            prev.map((n) => (n.id === node.id ? { ...n, position: originalPosition } : n)),
          );
        }
        return;
      }
      void callApiWithParameters("set_step_pos/", {
        run_name: runName,
        step_id: node.id,
        x: node.position.x,
        y: node.position.y,
      }).then(() => {
        navigateOrRefreshSteps();
      });
    },
    [navigateOrRefreshSteps, nodes, nodesOverlap, runName],
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
        void fetchEdges();
      });
    },
    [fetchEdges, notify, runName],
  );

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
      void fetchEdges();
    });
  }, [fetchEdges, notify, runName, selectedEdge]);

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
    <StyledRow>
      <StyledFlowColumn>
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
          <ReactFlow
            key={runName}
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            onNodeDragStart={onNodeDragStart}
            onNodeDragStop={onNodeDragStop}
            onConnect={onConnect}
            fitView
          >
            <Panel position="top-left">
              <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                <GrayButton onClick={onAutoLayout}>Tidy layout</GrayButton>
                <RedButton onClick={() => void deleteCurrentStep()}>Remove current step</RedButton>
                {selectedEdge && (
                  <RedButton onClick={removeCurrentConnection} isDisabled={!selectedEdge}>
                    Remove selected connection
                  </RedButton>
                )}
              </div>
            </Panel>

            <Panel position="top-right">
              {hoveredHandleMeta.isActive && (
                <div style={{ textAlign: "right" }}>
                  <p>{hoveredHandleMeta.direction}</p>
                  <p>{hoveredHandleMeta.type}</p>
                </div>
              )}
            </Panel>
          </ReactFlow>
        </StyledFlowCanvas>
      </StyledFlowColumn>

      <StyledDivider />

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
            // Quite a radical solution, but sadly works
            navigateOrRefreshSteps();
          }}
        />
      </StyledFormColumn>
    </StyledRow>
  );
};
