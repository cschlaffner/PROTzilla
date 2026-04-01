import dagre from "@dagrejs/dagre";
import type { Edge } from "@xyflow/react";

import type { StepNodeType } from "./StepNode";

const DAGRE_NODE_WIDTH = 260;
const DAGRE_NODE_HEIGHT = 72;
const DAGRE_NODE_SEP = 40;
const DAGRE_RANK_SEP = 80;
const DAGRE_RANK_DIR = "TB";
const COLLISION_MAX_ITERATIONS = 50;
const COLLISION_OVERLAP_THRESHOLD = 0.5;
const COLLISION_MARGIN = 12;

// "inspired" by https://reactflow.dev/examples/layout/node-collisions

export interface CollisionAlgorithmOptions {
  maxIterations: number;
  overlapThreshold: number;
  margin: number;
}

export type CollisionAlgorithm = (
  nodes: StepNodeType[],
  options?: Partial<CollisionAlgorithmOptions>,
) => StepNodeType[];

interface Box {
  x: number;
  y: number;
  width: number;
  height: number;
  moved: boolean;
  node: StepNodeType;
}

function getBoxesFromNodes(nodes: StepNodeType[], margin = 0): Box[] {
  const boxes: Box[] = new Array(nodes.length);

  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    boxes[i] = {
      x: node.position.x - margin,
      y: node.position.y - margin,
      width: (node.width ?? node.measured?.width ?? DAGRE_NODE_WIDTH) + margin * 2,
      height: (node.height ?? node.measured?.height ?? DAGRE_NODE_HEIGHT) + margin * 2,
      node,
      moved: false,
    };
  }

  return boxes;
}

export const layoutNodesWithDagre = (nodes: StepNodeType[], edges: Edge[]): StepNodeType[] => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({
    rankdir: DAGRE_RANK_DIR,
    nodesep: DAGRE_NODE_SEP,
    ranksep: DAGRE_RANK_SEP,
  });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: DAGRE_NODE_WIDTH,
      height: DAGRE_NODE_HEIGHT,
    });
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

// "inspired" by https://reactflow.dev/examples/layout/node-collisions

export const resolveCollisions: CollisionAlgorithm = (
  nodes: StepNodeType[],
  {
    maxIterations = COLLISION_MAX_ITERATIONS,
    overlapThreshold = COLLISION_OVERLAP_THRESHOLD,
    margin = COLLISION_MARGIN,
  }: Partial<CollisionAlgorithmOptions> = {},
): StepNodeType[] => {
  const boxes = getBoxesFromNodes(nodes, margin);

  for (let iter = 0; iter <= maxIterations; iter++) {
    let hasMoved = false;

    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const A = boxes[i];
        const B = boxes[j];

        // Calculate center positions
        const centerAX = A.x + A.width * 0.5;
        const centerAY = A.y + A.height * 0.5;
        const centerBX = B.x + B.width * 0.5;
        const centerBY = B.y + B.height * 0.5;

        // Calculate distance between centers
        const dx = centerAX - centerBX;
        const dy = centerAY - centerBY;

        // Calculate overlap along each axis
        const px = (A.width + B.width) * 0.5 - Math.abs(dx);
        const py = (A.height + B.height) * 0.5 - Math.abs(dy);

        // Check if there's significant overlap
        if (px > overlapThreshold && py > overlapThreshold) {
          A.moved = B.moved = hasMoved = true;
          // Resolve along the smallest overlap axis
          if (px < py) {
            // Move along x-axis
            const sx = dx > 0 ? 1 : -1;
            const moveAmount = (px / 2) * sx;
            A.x += moveAmount;
            B.x -= moveAmount;
          } else {
            // Move along y-axis
            const sy = dy > 0 ? 1 : -1;
            const moveAmount = (py / 2) * sy;
            A.y += moveAmount;
            B.y -= moveAmount;
          }
        }
      }
    }
    // Early exit if no overlaps were found
    if (!hasMoved) {
      break;
    }
  }

  return boxes.map((box) => {
    if (!box.moved) {
      return box.node;
    }

    return {
      ...box.node,
      position: {
        x: box.x + margin,
        y: box.y + margin,
      },
    };
  });
};
