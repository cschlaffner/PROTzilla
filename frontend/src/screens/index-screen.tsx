import React, {  useEffect, useState } from "react";
import { Col, Container, Row } from "react-grid-system";
import { styled } from "styled-components";
import { Navbar } from "../components/navbar";
import { useNavigate } from "react-router-dom";
import { Card } from "../components";


const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const StyledContainer = styled(Container)`
  padding: 15px;
  gap: 10px;
  display: flex;
  flex-direction: column;
`;

const StyledTemplateCard = styled(Card)`
  height: 300px;
`;

const StyledRunSelectionCard = styled(Card)`
  height: calc(100vh - 440px);
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

        <StyledRunSelectionCard title="Run Selection">Jannes</StyledRunSelectionCard>

      </StyledContainer>
    </div>
  );
};
