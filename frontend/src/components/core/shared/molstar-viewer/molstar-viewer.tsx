import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { DefaultPluginUISpec } from "molstar/lib/mol-plugin-ui/spec";
import React, { useEffect, useRef } from "react";

interface MolstarViewerProps {
  cifUrl: string;
}

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifUrl }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const pluginRef = useRef<PluginUIContext | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const plugin = new PluginUIContext(DefaultPluginUISpec());
    pluginRef.current = plugin;
    plugin.layout.setRoot(containerRef.current);

    return () => {
      pluginRef.current?.dispose();
      pluginRef.current = null;
    };
  }, [cifUrl]);

  return <div ref={containerRef} style={{ width: "100%", height: "600px" }} />;
};

export default MolstarViewer;
