import type { DefaultColoredIconType, IconType } from "@protzilla/core";
import { ContentText, DefaultColoredIcon, Icon } from "@protzilla/core";
import { defaultPalette } from "@protzilla/theme";
import { type SectionIDs, type Step, type StepID } from "@protzilla/utils";
import { Handle, Node, NodeProps, Position } from "@xyflow/react";
import type React from "react";
import { styled } from "styled-components";

import {
  handleCifIcon,
  handleConfidenceIcon,
  handleCrosslinkingIcon,
  handleDebugDataIcon,
  handleDnaIcon,
  handleFullDataIcon,
  handleMetadataIcon,
  handlePaeIcon,
  handlePeptidesIcon,
  handlePlddtIcon,
  handleProteinIcon,
  handlePsmIcon,
  handleSequencesIcon,
  handleStructureMetadataIcon,
} from "../../../core/shared/icon/icons";

type HandleDirection = "Input" | "Output" | "None";

export interface HoveredHandleMeta {
  isActive: boolean;
  direction: HandleDirection;
  type: string;
}

export interface StepNodeData extends Record<string, unknown> {
  step: Step;
  section: SectionIDs;
  isSelected: boolean;
  navigateOrRefreshSteps: (stepID?: StepID) => void;
  setHoveredHandleMeta: React.Dispatch<React.SetStateAction<HoveredHandleMeta>>;
}

export type StepNodeType = Node<StepNodeData, "step">;

type HandleIcon = React.ComponentType<React.SVGProps<SVGSVGElement>>;

const DATA_TYPE_ICON_MAP: Partial<Record<string, HandleIcon>> = {
  amino_acid_sequences_df: handleSequencesIcon,
  cif_df: handleCifIcon,
  confidence_df: handleConfidenceIcon,
  crosslinking_df: handleCrosslinkingIcon,
  debug_data: handleDebugDataIcon,
  fasta_df: handleSequencesIcon,
  full_data_df: handleFullDataIcon,
  gene_mapping_df: handleDnaIcon,
  metadata_df: handleMetadataIcon,
  pae_matrix: handlePaeIcon,
  peptide_df: handlePeptidesIcon,
  plddt_df: handlePlddtIcon,
  protein_df: handleProteinIcon,
  psm_df: handlePsmIcon,
  structure_metadata_df: handleStructureMetadataIcon,
};

const HANDLE_ICON_SIZE = 26;
const HANDLE_ICON_OFFSET = HANDLE_ICON_SIZE / 2;
const FALLBACK_TRIANGLE_SIZE = Math.round(HANDLE_ICON_SIZE * 0.6);

const triangleStyle = (direction: HandleDirection) => ({
  width: FALLBACK_TRIANGLE_SIZE,
  height: FALLBACK_TRIANGLE_SIZE,
  clipPath:
    direction === "Input" ? "polygon(50% 0,100% 100%,0 100%)" : "polygon(50% 100%,100% 0,0 0)",
  backgroundColor: "#1d1d1d",
});

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
    data.navigateOrRefreshSteps(data.step.id);
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
      {data.step.input_keys.map((input, index) => {
        const InputIcon = DATA_TYPE_ICON_MAP[input];
        return (
          <Handle
            key={index}
            type="target"
            position={Position.Top}
            id={input}
            style={{
              background: "none",
              border: "none",
              width: HANDLE_ICON_SIZE,
              height: HANDLE_ICON_SIZE,
              left: `${String((100 / (data.step.input_keys.length + 1)) * (index + 1))}%`,
              top: -HANDLE_ICON_OFFSET,
              transform: "translateX(-50%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onMouseEnter={() => {
              data.setHoveredHandleMeta({ isActive: true, direction: "Input", type: input });
            }}
            onMouseLeave={() => {
              data.setHoveredHandleMeta({ isActive: false, direction: "None", type: "None" });
            }}
          >
            {InputIcon ? (
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  backgroundColor: "#ffffff",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <InputIcon
                  style={{ width: "100%", height: "100%" }}
                  aria-hidden="true"
                  focusable="false"
                />
              </div>
            ) : (
              <div style={triangleStyle("Input")}></div>
            )}
          </Handle>
        );
      })}

      {/*Source (ouput) handles*/}
      {data.step.output_keys.map((output, index) => {
        const OutputIcon = DATA_TYPE_ICON_MAP[output];
        return (
          <Handle
            key={index}
            type="source"
            position={Position.Bottom}
            id={output}
            style={{
              background: "none",
              border: "none",
              width: HANDLE_ICON_SIZE,
              height: HANDLE_ICON_SIZE,
              left: `${String((100 / (data.step.output_keys.length + 1)) * (index + 1))}%`,
              bottom: -HANDLE_ICON_OFFSET,
              transform: "translateX(-50%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onMouseEnter={() => {
              data.setHoveredHandleMeta({ isActive: true, direction: "Output", type: output });
            }}
            onMouseLeave={() => {
              data.setHoveredHandleMeta({ isActive: false, direction: "None", type: "None" });
            }}
          >
            {OutputIcon ? (
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  backgroundColor: "#ffffff",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <OutputIcon
                  style={{ width: "100%", height: "100%" }}
                  aria-hidden="true"
                  focusable="false"
                />
              </div>
            ) : (
              <div style={triangleStyle("Output")}></div>
            )}
          </Handle>
        );
      })}
    </StyledNode>
  );
}
