import { CrosslinkerType } from "./crosslinker-processing";

export const CROSSLINKER_COLORS: Record<CrosslinkerType, number> = {
  [CrosslinkerType.ValidIntra]: 0xe03e00, // bright orange-red
  [CrosslinkerType.InvalidIntra]: 0xfca311, // pale yellow-orange
  [CrosslinkerType.ValidInter]: 0x8a2be2, // bright purple
  [CrosslinkerType.InvalidInter]: 0xd8b4ff, // pale violet
};
