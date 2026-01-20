import "@xyflow/react/dist/style.css";
import { useNotification } from "@protzilla/app";
import { BackendForm, FlexRow, Icon, RedButton, SecondaryButton } from "@protzilla/core";
import { color, spacing } from "@protzilla/theme";
import { callApiWithParameters, translateGlobalToSectionIndex } from "@protzilla/utils";
import { applyEdgeChanges, applyNodeChanges, Panel, ReactFlow } from "@xyflow/react";
import { useCallback, useEffect, useState } from "react";
import { styled } from "styled-components";

import { StepSelection } from "../step-selection";
import StepNode from "./StepNode.tsx";

const nodeTypes = { step: StepNode };

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
  const notify = useNotification();

  const onAddStep = () => {
    notify({ type: "success", message: "Successfully added step" });
    navigateOrRefreshSteps();
  };

  //
  // ReactFlow initialisation
  //

  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  // TODO: When do we want to propagate positions to the backend?
  // This function gets called wayy to frequently to use for that.
  // Maybe on every new step selection?
  const onNodesChange = useCallback((changes) => {
    setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot));
  }, []);
  const onEdgesChange = useCallback((changes) => {
    setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot));
  }, []);

  const getEdgesFromRunData = () => {
    // TODO: This needs to be implemented when the API provides sufficient data.
    return [];
  };

  const onConnect = useCallback(
    (params) => {
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
    [edges, navigateOrRefreshSteps],
  );

  // Mouse-Over info for each handle, displayed in the corner
  const [hoveredHandleMeta, setHoveredHandleMeta] = useState({
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

  useEffect(() => {
    console.log("Run Data", runData);
    const newNodes = [];
    let yOffset = 0;
    let flatStepIndex = 0;

    sections.forEach((section) => {
      section.steps.forEach((step, index) => {
        const isSelected =
          runData.current_section === section.id && runData.current_step_index === flatStepIndex;

        // Retain positions on redraw
        const oldMatchingNode = nodes.find((node) => node.id == step.id);
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
    setNodes(newNodes);
  }, [runData]); // TODO: eslint does not like this, but idk how to handle this properly

  const stepSelectionProps = {
    runName: runName,
    index: 0,
    onAddStep: onAddStep,
  };

  return (
    <StyledRow>
      <div style={{ width: "25vw", height: "100vh" }}>
        {/* Buttons for adding steps. TODO: Put these side-by-side*/}
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
            <RedButton onClick={deleteCurrentStep}>Remove current step</RedButton>
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
