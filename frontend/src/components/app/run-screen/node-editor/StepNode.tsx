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

// --- Constants ---
const NODE_WIDTH = 285;
const NODE_HEIGHT = 70;
const HANDLE_ICON_SIZE = 26;
const HANDLE_ICON_OFFSET = HANDLE_ICON_SIZE / 2;
const FALLBACK_TRIANGLE_SIZE = Math.round(HANDLE_ICON_SIZE * 0.6);

// --- Styled Components ---

const StyledNode = styled.div`
  width: ${NODE_WIDTH}px;
  height: ${NODE_HEIGHT}px;
  padding: 0 15px;
  display: flex;
  align-items: center;
  position: relative;
  border: 2px solid #1d1d1d;
  border-radius: 8px;
  background-color: white;
  box-sizing: border-box; /* Ensures padding doesn't affect the fixed width */
`;

const StatusIndicatorWrapper = styled.div`
  /* Removed absolute positioning */
  flex-shrink: 0;
  margin-right: 8px; /* Spacing between status and operation icon */
  display: flex;
  align-items: center;
  justify-content: center;

  /* Optional: Adjust size of status icon if needed */
  & > svg,
  & > span {
    width: 20px !important;
    height: 20px !important;
  }
`;

const OperationIconWrapper = styled.div`
  flex-shrink: 0;
  margin-right: 12px;

  /* Targeting the Icon component specifically to make it larger */
  & > svg,
  & > span {
    width: 40px !important;
    height: 40px !important;
  }
`;

const TextContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;

  /* Text wrapping logic */
  & span {
    white-space: normal;
    word-break: break-word;
    display: -webkit-box;
    -webkit-line-clamp: 2; /* Limits text to 2 lines to maintain node height */
    -webkit-box-orient: vertical;
    line-height: 1.2;
  }
`;

// --- Helpers & Maps ---

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

const triangleStyle = (direction: HandleDirection) => ({
  width: FALLBACK_TRIANGLE_SIZE,
  height: FALLBACK_TRIANGLE_SIZE,
  clipPath:
    direction === "Input" ? "polygon(50% 0,100% 100%,0 100%)" : "polygon(50% 100%,100% 0,0 0)",
  backgroundColor: "#1d1d1d",
});

export default function StepNode({ data }: NodeProps<StepNodeType>) {
  const onElementClick = () => {
    data.navigateOrRefreshSteps(data.step.id);
  };

  const nodeBgColour = data.isSelected ? defaultPalette.protzillaLightGray : "white";
  const nodeIcon = data.section as IconType;
  const statusIcon: DefaultColoredIconType = data.step.status;

  return (
    <StyledNode
      className="step-node"
      style={{ backgroundColor: nodeBgColour }}
      onClick={onElementClick}
    >
      {/* Status Indicator outside the node */}
      <StatusIndicatorWrapper>
        <DefaultColoredIcon icon={statusIcon} />
      </StatusIndicatorWrapper>

      {/* Larger Operation Icon */}
      <OperationIconWrapper>
        <Icon icon={nodeIcon} />
      </OperationIconWrapper>

      {/* Wrapped Text Content */}
      <TextContainer>
        <ContentText text={data.step.name} style={{ userSelect: "none", fontSize: "18px" }} />
      </TextContainer>

      {/* Input handles */}
      {data.step.input_keys.sort().map((input, index) => {
        const InputIcon = DATA_TYPE_ICON_MAP[input];
        return (
          <Handle
            key={`in-${String(index)}`}
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

      {/* Output handles */}
      {data.step.output_keys.sort().map((output, index) => {
        const OutputIcon = DATA_TYPE_ICON_MAP[output];
        return (
          <Handle
            key={`out-${String(index)}`}
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
