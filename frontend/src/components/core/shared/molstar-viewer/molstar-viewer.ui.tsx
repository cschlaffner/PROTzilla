import React from "react";

import { CrosslinkerType } from "./crosslinker-processing";
import { getCrosslinkerColor } from "./molstar-viewer.service";
import { LegendContainer } from "./styles";

export const LegendOverlay: React.FC = () => {
  return (
    <LegendContainer>
      <div>
        <span style={{ color: getCrosslinkerColor(CrosslinkerType.ValidIntra) }}>■</span>{" "}
        {CrosslinkerType.ValidIntra}{" "}
      </div>
      <div>
        <span style={{ color: getCrosslinkerColor(CrosslinkerType.InvalidIntra) }}>■</span>{" "}
        {CrosslinkerType.InvalidIntra}{" "}
      </div>
      <div>
        <span style={{ color: getCrosslinkerColor(CrosslinkerType.ValidInter) }}>■</span>{" "}
        {CrosslinkerType.ValidInter}{" "}
      </div>
      <div>
        <span style={{ color: getCrosslinkerColor(CrosslinkerType.InvalidInter) }}>■</span>{" "}
        {CrosslinkerType.InvalidInter}{" "}
      </div>
    </LegendContainer>
  );
};
