import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import React, { useEffect, useRef } from "react";
import "molstar/lib/mol-plugin-ui/skin/light.scss";

interface MolstarViewerProps {
  cifUrl: string;
}

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifUrl }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    let plugin: Awaited<ReturnType<typeof createPluginUI>>;

    const init = async (container: HTMLDivElement) => {
      plugin = await createPluginUI(container);

      const data = await plugin.builders.data.download(
        { url: cifUrl, isBinary: false },
        { state: { isGhost: true } },
      );

      const trajectory = await plugin.builders.structure.parseTrajectory(data, "mmcif");

      await plugin.builders.structure.hierarchy.applyPreset(trajectory, "default");
    };

    void init(containerRef.current);

    return () => {
      plugin.dispose();
    };
  }, [cifUrl]);

  return (
    <div ref={containerRef} style={{ width: "100%", height: "500px", position: "relative" }} />
  );
};

export default MolstarViewer;
