import type React from "react";

import { Run } from "@protzilla/utils";

export interface RunsTableProps extends React.HTMLAttributes<HTMLDivElement> {
  runs: Run[];
  filteredRuns: Run[];
  setRuns: React.Dispatch<React.SetStateAction<Run[]>>;
  openTagModal: React.Dispatch<React.SetStateAction<boolean>>;
  setSelectedRun: React.Dispatch<React.SetStateAction<Run>>;
}
