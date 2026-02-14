import "@xyflow/react/dist/style.css";
import { useNotification } from "@protzilla/app";
import { BackendForm, FlexRow, Icon, RedButton, SecondaryButton } from "@protzilla/core";
import { color, spacing } from "@protzilla/theme";
import type { Section, Step } from "@protzilla/utils";
import { callApiWithParameters, emptyRunData, SectionIDs, supportedSections, translateGlobalToSectionIndex } from "@protzilla/utils";
import type { Connection, Edge, EdgeChange, NodeChange, NodeTypes } from "@xyflow/react";
import { applyEdgeChanges, applyNodeChanges, Panel, ReactFlow } from "@xyflow/react";
import { useCallback, useEffect, useState } from "react";
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
  // Fallback. Future TODO: Make this cleaner
  if (runData == emptyRunData) {
    return <h1>Node Editor Fallback</h1>
  }

  const notify = useNotification();

  const onAddStep = () => {
    notify({ type: "success", title: "Step added", message: "Successfully added step" });
    navigateOrRefreshSteps();
  };

  //
  // ReactFlow initialisation
  //

  const [nodes, setNodes] = useState<StepNodeType[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);

  const onNodesChange = useCallback((changes: NodeChange<StepNodeType>[]) => {
    setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot));
  }, []);
  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot));
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

  const getEdgesFromRunData = useCallback(async (): Promise<Edge[]> => {
    const res = await callApiWithParameters("get_edges/", { run_name: runName });
    return res.data as Edge[];
  }, [runName]);

  const onEdgeClick = useCallback((_event: React.MouseEvent, edge: Edge) => {
    setSelectedEdge(edge);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedEdge(null);
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
      void getEdgesFromRunData().then((newEdges) => {
        setEdges(newEdges);
      });
    });
  }, [getEdgesFromRunData, notify, runName, selectedEdge]);

  const onConnect = useCallback(
    (params: Connection) => {
      console.log(params);
      void callApiWithParameters("connect_steps/", {
        run_name: runName,
        connection: params,
      }).then((response) => {
        notify({
          type: response.success ? "success" : "error",
          title: response.message.title,
          message: response.message.msg,
        });
        void getEdgesFromRunData().then((newEdges) => {
          setEdges(newEdges);
        });
      });
    },
    [getEdgesFromRunData, navigateOrRefreshSteps, notify, runName],
  );

  // Mouse-Over info for each handle, displayed in the corner
  const [hoveredHandleMeta, setHoveredHandleMeta] = useState<HoveredHandleMeta>({
    isActive: false,
    direction: "Input",
    type: "protein_df",
  });

  //
  // Run data
  //


  const deleteCurrentStep = async () => {
    await callApiWithParameters("delete_step/", {
      run_name: runName,
      step_iid: runData.current_step_iid,
    }).then((response) => {
      notify({
        type: response.success ? "success" : "error",
        title: response.message,
      });
    });
    navigateOrRefreshSteps();
  };

  const allSteps: Step[] = runData.displayed_steps;
  const currentSectionId = runData.current_section as SectionIDs;
  const currentSection = supportedSections.find((section) => section.id === currentSectionId);
  const currentStep = allSteps.find((step) => step.id === runData.current_step_iid)

  const currentStepCalculationStatus = currentStep.status;
  const buttonText =
    currentStepCalculationStatus === "complete"
      ? "Next"
      : currentSectionId === SectionIDs.Importing
        ? "Import"
        : "Calculate";

  useEffect(() => {
    console.log("Run Data", runData);
    const effectAllSteps = runData.displayed_steps;
    setNodes((nodesSnapshot) => {
      const newNodes: StepNodeType[] = [];
      let yOffset = 0;

      
      effectAllSteps.forEach((step: Step) => {
        const isSelected = runData.current_step_iid === step.id

        const oldMatchingNode = nodesSnapshot.find((node) => node.id == step.id);
        const savedPosition = step.visual_data?.node_position;
        const position = oldMatchingNode
          ? oldMatchingNode.position
          : savedPosition
            ? { x: savedPosition.x, y: savedPosition.y }
            : { x: 0, y: yOffset };

        newNodes.push({
          id: step.id,
          type: "step",
          position: position,
          data: {
            step: step,
            section: step.section,
            isSelected: isSelected,
            navigateOrRefreshSteps: navigateOrRefreshSteps,
            setHoveredHandleMeta: setHoveredHandleMeta,
          },
        });

        yOffset += 60;
      });
      return newNodes;
    });

    void getEdgesFromRunData().then((newEdges) => {
      setEdges(newEdges);
    });
  }, [currentSectionId, navigateOrRefreshSteps, runData]);

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
              <RedButton onClick={removeCurrentConnection} isDisabled={!selectedEdge}>
                Remove current connection
              </RedButton>
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

      {/* TODO: B250 add appropriate calls */}
      <StyledFormColumn>
        <BackendForm
          runName={runName}
          buttonText={buttonText}
          previousStepCalculationStatus={"complete"}
          currentStepCalculationStatus={currentStepCalculationStatus}
          current_step_iid={runData.current_step_iid}
          isLastStep={(!runData.recommended_next_step_iid)}
          onNext={() => {
            navigateOrRefreshSteps(runData.recommended_next_step_iid)
          }}
          onSubmit={onFormSubmit}
          onChange={() => {
            console.log("TODO: A vulture ate this callback! Come up with something better.");
          }}
        />
      </StyledFormColumn>
    </StyledRow>
  );
};
