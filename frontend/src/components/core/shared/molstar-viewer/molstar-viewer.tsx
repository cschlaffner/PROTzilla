import { SectionTitle } from "@protzilla/core";
import { createPluginUI } from "molstar/lib/mol-plugin-ui";
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { renderReact18 } from "molstar/lib/mol-plugin-ui/react18";
import React, { useEffect, useRef, useState } from "react";
import { styled } from "styled-components";
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
}

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifText }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const ErrorTitle = styled(SectionTitle)`
    color: ${({ theme }) => theme.colors.caution};
    * {
      color: inherit !important;
    }
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
  }, [cifText]);

  return (
    <Container>
      {isLoading && <SectionTitle baseComponent="h4" description="Structure is loading..." />}
      {error && <ErrorTitle baseComponent="h4" description={error} />}
      <CanvasWrapper ref={containerRef} />
    </Container>
  );
};

export default MolstarViewer;
