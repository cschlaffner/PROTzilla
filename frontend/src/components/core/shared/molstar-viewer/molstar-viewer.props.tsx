import { CrosslinkerInformation } from "./crosslinker-processing";
import { TrimeshLike } from "./molstar-trimesh-adapter";

export interface MolstarViewerProps {
  cifText: string;
  crosslinks?: CrosslinkerInformation[];
  polyhedron?: TrimeshLike;
}
