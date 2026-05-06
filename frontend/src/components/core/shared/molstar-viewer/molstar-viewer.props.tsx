import { CrosslinkerInformation } from "./crosslinker-processing";
import { TrimeshMesh } from "./molstar-trimesh-adapter";

export interface TrimeshShape {
  label: string;
  mesh: TrimeshMesh;
  color?: number;
  alpha?: number;
}

export interface MolstarViewerProps {
  cifText: string;
  crosslinks?: CrosslinkerInformation[];
  trimeshMeshes?: TrimeshShape[];
}
