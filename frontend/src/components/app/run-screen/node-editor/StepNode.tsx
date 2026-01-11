import {useCallback} from "react";
import { Node, NodeProps, Handle, Position} from '@xyflow/react';
import styled from 'styled-components'; 

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
  navigateOrRefreshSteps,
}, 'step'>;

const colorForSection = {
  "importing": "#8078bf",
  "data_preprocessing": "#78bf81",
  "data_analysis": "#bf9b78",
  "data_integration": "#bcbf78"
}

const defaultNodeBgColor = "#808080"; 

const StyledNode = styled.div`
  background-color: ${defaultNodeBgColor};
  padding: 10px;
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

  return(
    <StyledNode 
      className={`step-node`}
      style={{backgroundColor: `${colorForSection[data.section]}`}}
      onClick={onElementClick}
    >
      <DefaultColoredIcon 
        icon={icon as DefaultColoredIconType} 
        style={{ flexShrink: 0 }} 
      />
      <TextContainer>
          <ContentText text={data.step.name} style={{ userSelect: "none", whiteSpace: "nowrap" }} />
      </TextContainer>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} />
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} />
    </StyledNode>
  );
}
