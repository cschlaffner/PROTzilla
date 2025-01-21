import { styled } from "styled-components";

import {
  color,
  fontSize,
  fontWeight,
  radius,
  size,
  spacing,
} from "../../theme";
import { FlexColumn } from "../box";
import { NodeProps } from "./node.props";
import { Icon, iconColor } from "../icon";
import { Text } from "../text";

const NodeHeader = styled.div`
  align-items: center;
  box-sizing: border-box;
  background: ${color("primary")};
  border-top-left-radius: ${radius("default")};
  border-top-right-radius: ${radius("default")};
  display: flex;
  flex-direction: row;
  gap: ${spacing("small")};
  height: ${size("buttonHeight")};
  padding-left: ${spacing("medium")};
  width: ${size("navigationItemWidth")};

  .icon {
    ${iconColor("onPrimary")}
  }
`;

const NodeTitle = styled(Text)`
  color: ${color("onPrimary")};
  fontsize: ${fontSize("button")};
  fontweight: ${fontWeight("bold")};
`;

const NodeBody = styled.div`
  background: ${color("background")};
  box-sizing: border-box;
  border-width: 1px;
  border-style: solid;
  border-color: black;
  display: flex;
  flex-direction: column;
  width: ${size("navigationItemWidth")};
  height: ${size("navigationItemWidth")};
  padding-left: ${spacing("medium")};
  padding-right: ${spacing("medium")};
  border-bottom-left-radius: ${radius("default")};
  border-bottom-right-radius: ${radius("default")};
`;

const Sockets = styled.div`
  box-sizing: border-box;
  width: 100;
  height: ${size("navigationItemWidth")};
  border-width: 1px;
  border-style: solid;
  border-color: black;
`;

const Input = styled(Text)`
  text-align: left;
`;

/*const Output = styled(Text)`
  text-align: right;
`;*/


export const Node: React.FC<NodeProps> = ({
  icon,
  title,
  titleTx,
  titleData,
  titleComponents,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  inputSockets,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  outputSockets,
  ...rest
}) => (
  <FlexColumn {...rest}>
    <NodeHeader>
      {icon && <Icon className="icon" icon={icon} />}
      <NodeTitle
        text={title}
        tx={titleTx}
        txData={titleData}
        txComponents={titleComponents}
      />
    </NodeHeader>
    <NodeBody>
      <Sockets>
        <Input>
          text = {inputSockets[0].title}
        </Input>
        {
          inputSockets.map((
            {titleTx: itemTitle}
          ) => (
            <Input>
              text = {itemTitle}
            </Input>
          ))
        }
      </Sockets>
    </NodeBody>
  </FlexColumn>
);
