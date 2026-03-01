import "@xyflow/react/dist/style.css";
import { useNotification } from "@protzilla/app";
import { BackendForm, FlexRow, Icon, RedButton, SecondaryButton } from "@protzilla/core";
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
import { useCallback, useEffect, useMemo, useState } from "react";
import { styled } from "styled-components";

import { StepSelection } from "../step-selection";
import type { HoveredHandleMeta, StepNodeType } from "./StepNode";
import StepNode from "./StepNode";
import { NodeEditorProps } from "./node-editor.props";

const nodeTypes: NodeTypes = { step: StepNode };

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
    fetchEdges();
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

  const onNodeDragStop = useCallback(
    (_event: unknown, node: StepNodeType) => {
      void callApiWithParameters("set_step_pos/", {
        run_name: runName,
        step_id: node.id,
        x: node.position.x,
        y: node.position.y,
      }).then(() => {
        navigateOrRefreshSteps();
      });
    },
    [navigateOrRefreshSteps, runName],
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
        fetchEdges();
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
      fetchEdges();
    });
  }, [fetchEdges, notify, runName, selectedEdge]);

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
    return <h1>Node Editor Fallback</h1>;
  }

  const buttonText =
    currentStep.status === "complete"
      ? "Next"
      : runData.current_section as SectionIDs === SectionIDs.Importing
        ? "Import"
        : "Calculate";

  const stepSelectionProps = {
    runName: runName,
    onAddStep: onAddStep,
  };

  return (
    <StyledRow>
      <div style={{ width: "calc(25vw + 24px)", height: "100vh" }}>
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
          <Panel position="top-left">
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
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
      </div>

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
