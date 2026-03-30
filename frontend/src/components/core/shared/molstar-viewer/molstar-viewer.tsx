import { SectionTitle } from "@protzilla/core";
import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import { MolScriptBuilder as MS } from "molstar/lib/mol-script/language/builder";
import React, { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";

import { CrosslinkerInformation, CrosslinkType, generateCrosslinkCIF } from "./crosslink-struktur";
import "./molstar-theme.scss";

const Container = styled.div`
  width: 100%;
  height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
`;

const CanvasWrapper = styled.div`
  flex: 1;
  position: relative;
  top: 86px;
`;

interface MolstarViewerProps {
  cifText: string;
  crosslinks: CrosslinkerInformation[] | undefined;
}

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifText, crosslinks }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const LoadingTitle = styled(SectionTitle)`
    margin: 15px;
  `;

  const ErrorTitle = styled(SectionTitle)`
    color: ${({ theme }) => theme.colors.caution};
    * {
      color: inherit !important;
    }
    margin: 15px;
  `;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let plugin: PluginUIContext | null = null;

    const init = async () => {
      try {
        setIsLoading(true);
        setError(null);

        plugin = await createPluginUI({
          target: container,
          render: renderReact18,
        });

        if (!cifText) {
          throw new Error("No CIF data provided");
        }

        const data = await plugin.builders.data.rawData({
          data: cifText,
          label: "structure",
        });

        const trajectory = await plugin.builders.structure.parseTrajectory(data, "mmcif");
        await plugin.builders.structure.hierarchy.applyPreset(trajectory, "default");

        if (crosslinks !== undefined) {
          const { crosslinkerCifText: crosslinkerCifText, crosslinkerGroups: crosslinkerGroups } =
            generateCrosslinkCIF(cifText, crosslinks);

          const lineData = await plugin.builders.data.rawData({
            data: crosslinkerCifText,
            label: "line",
          });
          const lineTrajectory = await plugin.builders.structure.parseTrajectory(lineData, "mmcif");
          const lineModel = await plugin.builders.structure.createModel(lineTrajectory);
          const lineStructure = await plugin.builders.structure.createStructure(lineModel);

          const CROSSLINKER_COLORS = {
            [CrosslinkType.ValidIntra]: 0xe03e00, // kräftiges orange-rot
            [CrosslinkType.InvalidIntra]: 0xfca311, // blasses gelb-orange
            [CrosslinkType.ValidInter]: 0x8a2be2, // kräftiges lila
            [CrosslinkType.InvalidInter]: 0xd8b4ff, // blasses lila
          };

          for (const type of Object.values(CrosslinkType)) {
            const atomIds = crosslinkerGroups[type];

            const expression = MS.struct.generator.atomGroups({
              "atom-test": MS.core.set.has([MS.set(...atomIds), MS.ammp("label_atom_id")]),
            });

            const component = await plugin.builders.structure.tryCreateComponentFromExpression(
              lineStructure,
              expression,
              type,
            );

            if (component) {
              await plugin.builders.structure.representation.addRepresentation(component, {
                type: "line",
                color: "uniform",
                colorParams: { value: CROSSLINKER_COLORS[type] },
              });
            }
          }
        }

        setIsLoading(false);
      } catch (err: unknown) {
        console.error("MolstarViewer Error:", err);
        const message = err instanceof Error ? err.message : String(err);
        setError(message);
        setIsLoading(false);
      }
    };

    void init();

    return () => {
      if (plugin !== null) {
        try {
          plugin.dispose();
        } catch (disposeErr) {
          console.warn("Error disposing Molstar plugin:", disposeErr);
        }
      }
    };
  }, [cifText, crosslinks]);

  return (
    <Container>
      {isLoading && <LoadingTitle baseComponent="h4" description="Structure is loading..." />}
      {error && <ErrorTitle baseComponent="h4" description={error} />}
      <CanvasWrapper ref={containerRef} />
    </Container>
  );
};

export default MolstarViewer;
