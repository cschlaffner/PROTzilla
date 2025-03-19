import React from "react";
import { Container } from "react-grid-system";
import { styled } from "styled-components";
import { Navbar } from "../components/navbar";
import { useNavigate } from "react-router-dom";
import { Card } from "../components";
import { size, spacing } from "../theme";

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const StyledContainer = styled(Container)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  display: flex;
  flex-direction: column;
`;

const StyledTemplateCard = styled(Card)`
  height: ${size("templateSelectionHeight")};
`;

const StyledRunSelectionCard = styled(Card)`
  height: calc(
    100vh -
      (
        ${spacing("navbarHeight")} + 7 * ${spacing("small")} +
          ${size("templateSelectionHeight")}
      )
  );
  min-height: ${size("runSelectionMinHeight")};
`;

export const IndexScreen: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div>
      <StyledNavbar
        allowRunEdit={false}
        onNavigateHome={() => navigate("/")}
        onOpenSettings={() => {}}
        onOpenHelp={() => {}}
      />

      <StyledContainer fluid>
        <StyledTemplateCard title="Template Workflows">NEIN</StyledTemplateCard>

        <StyledRunSelectionCard title="Run Selection">
          Jannes
        </StyledRunSelectionCard>
      </StyledContainer>
    </div>
  );
};
