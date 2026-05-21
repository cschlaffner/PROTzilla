import { useNotification } from "@protzilla/app";
import { SectionTitle } from "@protzilla/core";
import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import React, { useEffect, useRef, useState } from "react";

import { MolstarViewerProps } from "./molstar-viewer.props";
import {
  addCrosslinks,
  handleError,
  initCrosslinkColors,
  overrideLabels,
} from "./molstar-viewer.service";
import { LegendOverlay } from "./molstar-viewer.ui";
import { CanvasWrapper, Container } from "./styles";
import "molstar/lib/mol-plugin-ui/skin/base/base.scss";

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifText, crosslinks }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const notify = useNotification();

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let plugin: PluginUIContext | null = null;

    const init = async () => {
      try {
        setIsLoading(true);

        if (!cifText) {
          throw new Error("No CIF data provided");
        }

        // initialize Molstar
        plugin = await createPluginUI({
          target: container,
          render: renderReact18,
        });

        // load structure
        const data = await plugin.builders.data.rawData({
          data: cifText,
          label: "structure",
        });
        const trajectory = await plugin.builders.structure.parseTrajectory(data, "mmcif");
        await plugin.builders.structure.hierarchy.applyPreset(trajectory, "default");

        // add crosslinks to structure, if available
        if (crosslinks !== undefined) {
          const crosslinkColors = await initCrosslinkColors();
          await addCrosslinks(plugin, cifText, crosslinks, crosslinkColors);
          overrideLabels(plugin, crosslinkColors);
        }

        setIsLoading(false);
      } catch (error: unknown) {
        handleError(error, "MolstarViewer Error:", notify);
        setIsLoading(false);
      }
    };

    void init();

    return () => {
      if (plugin !== null) {
        try {
          plugin.dispose();
        } catch (disposeError) {
          handleError(disposeError, "Error disposing Molstar plugin:", notify);
        }
      }
    };
  }, [cifText, crosslinks, notify]);

  return (
    <Container>
      {isLoading && (
        <SectionTitle baseComponent="h4" description="Structure visualisation is loading..." />
      )}
      <CanvasWrapper ref={containerRef} />

      {crosslinks !== undefined && <LegendOverlay />}
    </Container>
  );
};

export default MolstarViewer;
