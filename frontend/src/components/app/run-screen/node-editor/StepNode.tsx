import type { DefaultColoredIconType, IconType } from "@protzilla/core";
import { ContentText, DefaultColoredIcon, Icon } from "@protzilla/core";
import { defaultPalette } from "@protzilla/theme";
import { type SectionIDs, type SelectedStep, type Step } from "@protzilla/utils";
import { Handle, Node, NodeProps, Position } from "@xyflow/react";
import type React from "react";
import { styled } from "styled-components";

type DataTypeKey = "peptide_df" | "protein_df" | "metadata_df";
type HandleDirection = "Input" | "Output" | "None";

export interface HoveredHandleMeta {
  isActive: boolean;
  direction: HandleDirection;
  type: DataTypeKey | "None";
}

export interface StepNodeData extends Record<string, unknown> {
  step: Step;
  step_index_within_section: number;
  section: SectionIDs;
  isSelected: boolean;
  navigateOrRefreshSteps: (selectedStep?: SelectedStep) => void;
  setHoveredHandleMeta: React.Dispatch<React.SetStateAction<HoveredHandleMeta>>;
}

export type StepNodeType = Node<StepNodeData, "step">;

// TODO: I don't like this method of indication,
// not very inclusive (color blindness).
// It should work for the initial draft though.
const DATA_TYPE_COLOR_INDICATORS: Record<DataTypeKey, string> = {
  peptide_df: "#BF1E74",
  protein_df: "#BF1E2E",
  metadata_df: "#2E1EBF",
};

const StyledNode = styled.div`
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 15px;
  padding-bottom: 15px;
  display: flex;
  align-itmes: center;
  position: relative;
  border: 2px solid black;
  border-radius: 5px;
`;

const TextContainer = styled.div`
  display: flex;
  gap: 5px;
  marginleft: "auto";
  max-width: 225px;
  whitespace: normal;
  line-height: 150%;
  max-height: 4.5em;
`;

export default function StepNode({ data }: NodeProps<StepNodeType>) {
  // const onClick = useCallback((evt) => {
  //   console.log(evt.target.value);
  // }, []);

  const onElementClick = () => {
    console.log(data.step.name); // TODO: still required?
    data.navigateOrRefreshSteps({
      section: data.section,
      index: data.step_index_within_section,
    });
  };

  const icon: DefaultColoredIconType = data.step.status;
  const nodeBgColour = data.isSelected ? defaultPalette.protzillaLightGray : "";

  return (
    <StyledNode
      className={`step-node`}
      style={{ backgroundColor: nodeBgColour }}
      onClick={onElementClick}
    >
      <Icon icon={data.section as IconType} style={{ flexShrink: 0, marginRight: "10px" }} />
      <DefaultColoredIcon icon={icon} style={{ flexShrink: 0 }} />
      <TextContainer style={{ marginLeft: "5px" }}>
        <ContentText
          text={`${data.step.method_name} : ${data.step.name}`}
          style={{ userSelect: "none" }}
        />
      </TextContainer>

      {/*Target (input) handles*/}
      {data.step.input_keys.map((input, index) => (
        <Handle
          key={index}
          type="target"
          position={Position.Top}
          id={input}
          style={{
            background: "none",
            border: "none",
            width: "1em",
            height: "1em",
            left: `${String((100 / (data.step.input_keys.length + 1)) * (index + 1))}%`,
            transform: "translateX(-50%)",
          }}
          onMouseEnter={() => {
            data.setHoveredHandleMeta({ isActive: true, direction: "Input", type: input });
          }}
          onMouseLeave={() => {
            data.setHoveredHandleMeta({ isActive: false, direction: "None", type: "None" });
          }}
        >
          <div
            style={{
              width: "15px",
              height: "15px",
              clipPath: "polygon(50% 100%,100% 0,0 0)",
              backgroundColor: DATA_TYPE_COLOR_INDICATORS[input],
            }}
          ></div>
        </Handle>
      ))}

      {/*Source (ouput) handles*/}
      {data.step.output_keys.map((output, index) => (
        <Handle
          key={index}
          type="source"
          position={Position.Bottom}
          id={output}
          style={{
            background: "none",
            border: "none",
            width: "15px",
            height: "15px",
            marginBottom: "1px",
            left: `${String((100 / (data.step.output_keys.length + 1)) * (index + 1))}%`,
            transform: "translateX(-50%)",
          }}
          onMouseEnter={() => {
            data.setHoveredHandleMeta({ isActive: true, direction: "Output", type: output });
          }}
          onMouseLeave={() => {
            data.setHoveredHandleMeta({ isActive: false, direction: "None", type: "None" });
          }}
        >
          <div
            style={{
              width: "15px",
              height: "15px",
              clipPath: "polygon(50% 100%,100% 0,0 0)",
              backgroundColor: DATA_TYPE_COLOR_INDICATORS[output],
            }}
          ></div>
        </Handle>
      ))}
    </StyledNode>
  );
}
