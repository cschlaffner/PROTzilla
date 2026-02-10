import React, { useEffect, useRef } from "react";

import { MolstarViewerProps } from "./molstar-viewer.props";
//import { Viewer } from "molstar/lib/molstar";

const MolstarViewer: React.FC<MolstarViewerProps> = ({ cifUrl }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    /*const viewer = new Viewer(containerRef.current, {
      layoutIsExpanded: true,
      layoutShowControls: true,
      layoutShowSequence: true,
      layoutShowLog: false,
    });

    viewer.loadStructureFromUrl(cifUrl, "mmCIF");

    return () => viewer.dispose();
    */
  }, [cifUrl]);

  return <div ref={containerRef} style={{ width: "100%", height: "600px" }} />;
};

export default MolstarViewer;
