import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { SectionTitle } from "../components";
import { Navbar } from "../components/navbar";

export const EmptyRunScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [runName] = useState<string>(location.state?.existingRun);

  return (
    <div>
      <Navbar
        title={runName}
        titleTx={runName}
        onNavigateHome={() => {
          void navigate("/");
        }}
        onOpenSettings={() => {
          void navigate("/");
        }}
        onOpenHelp={() => {
          void navigate("/");
        }}
        allowRunEdit={true}
      />
      <SectionTitle
        baseComponent={"h3"}
        title={
          "dummy run screen for this component, will not be pushed with this PR"
        }
        description={""}
      />
    </div>
  );
};
