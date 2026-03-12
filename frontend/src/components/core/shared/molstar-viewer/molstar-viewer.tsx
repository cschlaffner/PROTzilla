import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import React, { useEffect, useRef, useState } from "react";
//import "molstar/lib/mol-plugin-ui/skin/blue.scss";
import "./molstar-theme.scss";

interface MolstarViewerProps {
  cifUrl?: string;
  cifText?: string;
}

//maybe the logic for loading the structure data from the .cif-file should be moved up e.g. into run-screen in the future
const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifUrl, cifText }) => {
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

        plugin = await createPluginUI({
          target: container,
          render: renderReact18,
        });

        let cifData: string;

        if (cifText) {
          cifData = cifText;
        } else if (cifUrl) {
          const response = await fetch(cifUrl);
          if (!response.ok)
            throw new Error(`Error when loading CIF-file: ${response.status.toString()}`);
          cifData = await response.text();
        } else {
          throw new Error("No CIF data provided");
        }

        const data = await plugin.builders.data.rawData({
          data: cifData,
          label: "structure",
        });

        const trajectory = await plugin.builders.structure.parseTrajectory(data, "mmcif");
        await plugin.builders.structure.hierarchy.applyPreset(trajectory, "default");

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
  }, [cifUrl]);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative", border: "1px solid #ccc" }}>
      {isLoading && (
        <div style={{ position: "absolute", top: 0, left: 0 }}>Structure is loading...</div>
      )}
      {error && <div style={{ color: "red", position: "absolute", top: 0, left: 0 }}>{error}</div>}
      <div ref={containerRef} style={{ width: "100%", height: "100%", position: "relative" }} />
    </div>
  );
};

export default MolstarViewer;
