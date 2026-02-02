import "@xyflow/react/dist/style.css";
import { useNotification } from "@protzilla/app";
import { BackendForm, FlexRow, Icon, RedButton, SecondaryButton } from "@protzilla/core";
import { color, spacing } from "@protzilla/theme";
import type { Section, Step } from "@protzilla/utils";
import { callApiWithParameters, SectionIDs, translateGlobalToSectionIndex } from "@protzilla/utils";
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
      });
    },
    [runName],
  );

  const getEdgesFromRunData = (): Edge[] => {
    // TODO: This needs to be implemented when the API provides sufficient data.
    return [];
  };

  const onConnect = useCallback(
    (params: Connection) => {
      console.log(params);
      // TODO: Implement this in API
      // await callApiWithParameters("connect_steps/", {
      //   run_name: runName,
      //   connection: params,
      // }).then((response) => {
      //   notify({
      //     type: response.success ? "success" : "error",
      //     title: response.message,
      //   });
      // });
      navigateOrRefreshSteps();
      setEdges(getEdgesFromRunData());
    },
    [navigateOrRefreshSteps],
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

  const sections: Section[] = runData.displayed_steps;
  const currentSectionId = runData.current_section as SectionIDs;
  const currentSection = sections.find((section) => section.id === currentSectionId);

  const currentStepCalculationStatus = currentSection?.steps[runData.current_step_index]?.status;
  const buttonText =
    currentStepCalculationStatus === "complete"
      ? "Next"
      : currentSectionId === SectionIDs.Importing
        ? "Import"
        : "Calculate";

  useEffect(() => {
    console.log("Run Data", runData);
    const effectSections = runData.displayed_steps;
    setNodes((nodesSnapshot) => {
      const newNodes: StepNodeType[] = [];
      let yOffset = 0;
      let flatStepIndex = 0;

      effectSections.forEach((section: Section) => {
        section.steps.forEach((step: Step, index: number) => {
          const isSelected =
            currentSectionId === section.id && runData.current_step_index === flatStepIndex;

          // Retain positions on redraw
          const oldMatchingNode = nodesSnapshot.find((node) => node.id == step.id);
          const position = oldMatchingNode ? oldMatchingNode.position : { x: 0, y: yOffset };

          newNodes.push({
            id: step.id,
            type: "step",
            position: position,
            data: {
              step: step,
              step_index_within_section: index,
              section: section.id,
              isSelected: isSelected,
              navigateOrRefreshSteps: navigateOrRefreshSteps,
              setHoveredHandleMeta: setHoveredHandleMeta,
            },
          });

          flatStepIndex += 1;
          yOffset += 60;
        });
      });
      return newNodes;
    });
  }, [currentSectionId, navigateOrRefreshSteps, runData]);

  const stepSelectionProps = {
    runName: runName,
    index: 0,
    onAddStep: onAddStep,
  };

  return (
    <StyledRow>
      <div style={{ width: "calc(25vw + 24px)", height: "100vh" }}>
        <StyledStepButtonsRow>
          {sections.map((section) => (
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
          onNodeDragStop={onNodeDragStop}
          onConnect={onConnect}
          fitView
        >
          <Panel position="top-left">
            <RedButton onClick={() => void deleteCurrentStep()}>Remove current step</RedButton>
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
            sections
              .map((section) => section.steps.length)
              .reduce((acc: number, val: number) => acc + val, 0) -
              1
          }
          onNext={() => {
            console.log("TODO: A vulture ate this callback! Come up with something better.");
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
