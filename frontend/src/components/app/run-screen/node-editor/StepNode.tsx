import {useCallback} from "react";
import { Node, NodeProps, Handle, Position} from '@xyflow/react';
import styled from 'styled-components'; 
import { Icon } from "@protzilla/core";
import { defaultPalette } from "@protzilla/theme";

import {
  DefaultColoredIcon,
  ContentText,
  CollapsibleLabel,
  DefaultColoredIconType,
} from "@protzilla/core";

type StepNode = Node<{ 
  step: object,
  step_index_within_section: number,
  section: string,
  isSelected: boolean,
  navigateOrRefreshSteps,
}, 'step'>;

// TODO: remove?
const colorForSection = {
  "importing": "#aeacbf",
  "data_preprocessing": "#acbfae",
  "data_analysis": "#bfb5ac",
  "data_integration": "#bebfac"
}

const StyledNode = styled.div`
  padding: 10px;
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

export default function StepNode({ data }: NodeProps<StepNode>) {
  const onClick = useCallback((evt) => {
    console.log(evt.target.value);
  }, []);

  const isConnectable = true;

  const onElementClick = (event: any) => {
    console.log(data.step.name)
    data.navigateOrRefreshSteps({
      section: data.section,
      index: data.step_index_within_section
    })
  }

  const icon = data.step.status;
  const node_bg_color = (data.isSelected ? defaultPalette["protzillaLightGray"] : "");

  return(
    <StyledNode 
      className={`step-node`}
      style={{backgroundColor: node_bg_color}}
      onClick={onElementClick}
      isSelected={data.isSelected}
    >
      <Icon icon={data.section} style={{ flexShrink: 0, marginRight: "10px" }} />
      <DefaultColoredIcon 
        icon={icon as DefaultColoredIconType} 
        style={{ flexShrink: 0 }} 
      />
      <TextContainer style={{marginLeft: "5px"}}>
          <ContentText text={data.step.name} style={{ userSelect: "none", whiteSpace: "nowrap" }} />
      </TextContainer>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} />
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} />
    </StyledNode>
  );
}
