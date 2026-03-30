import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import React, { useEffect, useRef, useState } from "react";

import { MolstarViewerProps } from "./molstar-viewer.props";
import { addCrosslinks } from "./molstar-viewer.service";
import { CanvasWrapper, Container, ErrorTitle, LoadingTitle } from "./styles";
import "./molstar-theme.scss";

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifText, crosslinks }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let plugin: PluginUIContext | null = null;

    const init = async () => {
      try {
        setIsLoading(true);
        setError(null);

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

        // add crosslinks to structure
        if (crosslinks !== undefined) {
          await addCrosslinks(plugin, cifText, crosslinks);
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
