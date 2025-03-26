import type React from "react";

import { Run } from "../../utils";

export interface RunsTableProps
  extends React.HTMLAttributes<HTMLDivElement> {
    runs: Run[];
    setRuns: React.Dispatch<React.SetStateAction<Run[]>>;
    openModal: React.Dispatch<React.SetStateAction<boolean>>;
    setSelectedRun: React.Dispatch<React.SetStateAction<Run>>;
  }