import React from "react";

import { CrosslinkerType } from "./crosslinker-processing";
import { CROSSLINK_DEFAULT_COLORS, CrosslinkColors } from "./molstar-viewer.config";
import { initCrosslinkColors } from "./molstar-viewer.service";
import { LegendContainer } from "./styles";

const legendEntries = Object.values(CrosslinkerType);

export const LegendOverlay: React.FC = () => {
  const [crosslinkerColors, setCrosslinkerColors] =
    React.useState<CrosslinkColors>(CROSSLINK_DEFAULT_COLORS);

  React.useEffect(() => {
    void initCrosslinkColors().then(setCrosslinkerColors);
  }, []);

  return (
    <LegendContainer>
      {legendEntries.map((entry) => (
        <div key={entry}>
          <span
            style={{
              color: `#${crosslinkerColors[entry].toString(16).padStart(6, "0")}`,
            }}
          >
            ■
          </span>{" "}
          {entry}
        </div>
      ))}
    </LegendContainer>
  );
};
