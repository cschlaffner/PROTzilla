import dagre from "@dagrejs/dagre";
import type { Edge } from "@xyflow/react";

import type { StepNodeType } from "./StepNode";

const DAGRE_NODE_WIDTH = 260;
const DAGRE_NODE_HEIGHT = 72;
const DAGRE_NODE_SEP = 40;
const DAGRE_RANK_SEP = 80;
const DAGRE_RANK_DIR = "TB";

export const layoutNodesWithDagre = (nodes: StepNodeType[], edges: Edge[]): StepNodeType[] => {
  if (nodes.length === 0) return nodes;

  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({
    rankdir: DAGRE_RANK_DIR,
    nodesep: DAGRE_NODE_SEP,
    ranksep: DAGRE_RANK_SEP,
  });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: DAGRE_NODE_WIDTH, height: DAGRE_NODE_HEIGHT });
  });
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  return nodes.map((node) => {
    const layoutedNode = dagreGraph.node(node.id);
    if (!layoutedNode) return node;

    return {
      ...node,
      position: {
        x: layoutedNode.x - DAGRE_NODE_WIDTH / 2,
        y: layoutedNode.y - DAGRE_NODE_HEIGHT / 2,
      },
    };
  });
};
