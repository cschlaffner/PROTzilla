import React, { useEffect, useState, useRef} from "react";
import { Container } from "react-grid-system";
import { styled } from "styled-components";
import { Navbar } from "../components/navbar";
import { useNavigate } from "react-router-dom";
import { Card, Workflow } from "../components";
import { size, spacing } from "../theme";
import { callApi } from "../utils";

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

const StyledWorkflowContainer = styled(Container)`
  display: flex;
  overflow-x: hidden;

  scrollbar-width: thin;
  scrollbar-color: #888 transparent;

  &::-webkit-scrollbar {
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }
  &:hover {
    overflow-x: auto;
  }
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
  const [workflows, setWorkflows] = useState([]);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      const data = await callApi("workflow_name_list/");
      if (data) {
        console.log(data);
        setWorkflows(data);
        }
      }

    void fetchData();
  }, []);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleWheelScroll = (event: WheelEvent) => {
      event.preventDefault();
      container.scrollLeft += event.deltaY; // Convert vertical scroll to horizontal
    };

    container.addEventListener("wheel", handleWheelScroll);
    return () => container.removeEventListener("wheel", handleWheelScroll);
  }, []);

  return (
    <div>
      <StyledNavbar
        allowRunEdit={false}
        onNavigateHome={() => navigate("/")}
        onOpenSettings={() => {}}
        onOpenHelp={() => {}}
      />

      <StyledContainer fluid>
      <StyledTemplateCard title="Template Workflows">
        <StyledWorkflowContainer ref={scrollContainerRef}>
          {workflows.map((workflow) => (
            <Workflow
              key={workflow}
              icon="add"
              workflow={workflow}
              onPress={() => {}}
            />
          ))}
        </StyledWorkflowContainer>
      </StyledTemplateCard>

        <StyledRunSelectionCard title="Run Selection">
          Jannes
        </StyledRunSelectionCard>
      </StyledContainer>
    </div>
  );
};
