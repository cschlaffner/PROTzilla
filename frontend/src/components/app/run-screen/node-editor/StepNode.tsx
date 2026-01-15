import {useCallback, useState} from "react";
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
  setHoveredHandleMeta
}, 'step'>;

// TODO: I don't like this method of indication,
// not very inclusive (color blindness).
// It should work for the initial draft though.
const data_type_color_indicators = {
  "peptide_df": "#BF1E74",
  "protein_df": "#BF1E2E",
  "meta_df": "#2E1EBF",
}

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

  // TODO: Integrate API. This is just a dummy in/out setup rn
  const step_inputs = ["peptide_df", "protein_df", "meta_df"];
  const step_outputs = ["peptide_df", "protein_df"];

  // TODO: Display tooltip for each handle (can't hurt)
  // I advocate for something in a fixed corner to avoid mess
  const handleMouseEnter = (text, event) => {
    console.log(text);
  };
  const handleMouseLeave = () => {
  };


  // TODO: The icons are quite messed up (especially the hitboxes and alignment)
  // Might want to fix that
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
          <ContentText 
            text={`${data.step.method_name} : ${data.step.name}`} 
            style={{ userSelect: "none", }} 
          />
      </TextContainer>

      {/*Target (input) handles*/}
      {step_inputs.map((input, index) => (
        <Handle
          key={index}
          type="target"
          position="top"
          id={`input-${input}-${index}`}
          style={{
            background: 'none',
            border: 'none',
            width: '1em',
            height: '1em',
            left: `${(100 / (step_inputs.length + 1)) * (index + 1)}%`,
            transform: 'translateX(-50%)',
          }}
          onMouseEnter={(e) => data.setHoveredHandleMeta(
            {"isActive": true, "direction": "Input", "type": input})}
          onMouseLeave={(e) => data.setHoveredHandleMeta(
            {"isActive": false, "direction": "None", "type": "None"})}
        >
        <div style={{
          width: '15px',
          height: '15px',
          clipPath: 'polygon(50% 100%,100% 0,0 0)',
          backgroundColor: data_type_color_indicators[input] || 'red',
        }}>
        </div>
        </Handle>
      ))}

      {/*Source (ouput) handles*/}
      {step_outputs.map((output, index) => (
        <Handle
          key={index}
          type="source"
          position="bottom"
          id={`output-${output}-${index}`}
          style={{
            background: 'none',
            border: 'none',
            width: '15px',
            height: '15px',
            marginBottom: '1px',
            left: `${(100 / (step_outputs.length + 1)) * (index + 1)}%`,
            transform: 'translateX(-50%)',
          }}
        onMouseEnter={(e) => data.setHoveredHandleMeta(
          {"isActive": true, "direction": "Output", "type": output})}
        onMouseLeave={(e) => data.setHoveredHandleMeta(
          {"isActive": false, "direction": "None", "type": "None"})}
        >
        <div style={{
          width: '15px',
          height: '15px',
          clipPath: 'polygon(50% 100%,100% 0,0 0)',
          backgroundColor: data_type_color_indicators[output] || 'red',
        }}>
        </div>
        </Handle>
      ))}
    </StyledNode>
  );
}
