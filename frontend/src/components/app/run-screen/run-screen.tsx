import { ListEditor, Navbar, PlotDownloadSettings } from "@protzilla/app";
import {
  CSVButton,
  DataTable,
  FlexColumn,
  FlexRow,
  PlotComponent,
  SecondaryButton,
  SectionTitle,
  SwitchCard,
} from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing, useTheme } from "@protzilla/theme";
import {
  callApiWithParameters,
  dummyTextComponent1,
  emptyRunData,
  footerMessages,
  SelectedStep,
  Table,
} from "@protzilla/utils";
import { Figure } from "plotly.js";
import React, { useCallback, useEffect, useState } from "react";
import { Col } from "react-grid-system";
import { useLocation, useNavigate } from "react-router-dom";
import { styled } from "styled-components";

const StyledNavbar = styled(Navbar)`
  position: sticky;
  top: 0;
  z-index: 1000;
`;
const StyledCardRow = styled(FlexRow)`
  padding: ${spacing("small")};
  gap: ${spacing("small")};
  flex: 1;
  height: 100%;
`;

const StyledFlexColumn = styled(FlexColumn)`
  height: 100%;
`;

const StyledCol = styled(Col)`
  display: flex;
  flex-direction: column;
  min-width: 0;
`;

const StyledListSwitchCard = styled(SwitchCard)`
  height: 100%;
`;

const StyledContentContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: ${spacing("small")};
`;

const StyledContentDiv = styled.div`
  display: flex;
  flex-direction: column;
`;

const FooterText = styled.div`
  text-align: center;
  padding: ${spacing("small")};
  font-size: 14px;
  color: gray;
  width: 100%;
`;

export const RunScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  const randomMessage = footerMessages[Math.floor(Math.random() * footerMessages.length)];
  const runName = location.state?.runName;

  const [runData, setRunData] = useState(emptyRunData);
  const [plots, setPlots] = useState<Figure[]>();
  const [selectedPlot, setSelectedPlot] = useState<Figure>({ data: [], layout: {} });
  const [tableData, setTableData] = useState<Table[]>();

  const [isDownloadModalOpen, openDownloadModal, closeDownloadModal] = useToggleableState(false);

  const handleStepSelection = (selectedStep: SelectedStep | undefined) => {
    if (selectedStep) {
      void callApiWithParameters("navigate_to_step/", {
        run_name: runName,
        section: selectedStep.section,
        index: String(selectedStep.index),
      }).then(() => {
        void getRunData();
        void getStepPlots();
        void getStepTable();
      });
    }
  };

  const getRunData = useCallback(async () => {
    const response = await callApiWithParameters("get_run_data/", {
      run_name: runName,
    });
    if (response) {
      setRunData(response.data);
    }
  }, [runName]);

  const getStepPlots = useCallback(async () => {
    const response = await callApiWithParameters("get_step_plots/", {
      run_name: runName,
    });
    if (response) {
      const data = response.data;

      const rawPlots = [];
      if (data.length > 0) {
        for (const plot of data) {
          rawPlots.push(JSON.parse(plot));
        }
      }

      setPlots(rawPlots);
    }
  }, [runName]);

  const getStepTable = useCallback(async () => {
    const response = await callApiWithParameters("get_step_table/", {
      run_name: runName,
    });
    if (response) {
      const data = response.data;
      setTableData(data);
    }
  }, [runName]);

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([getRunData(), getStepPlots(), getStepTable()]);
    };

    void fetchData();
  }, [getRunData, getStepPlots, getStepTable]);

  const onFormSubmit = () => {
    void getRunData();
    void getStepPlots();
    void getStepTable();
  };

  const handleDownloadPlot = (plot: Figure) => {
    setSelectedPlot(plot);
    openDownloadModal();
  };

  const plotComponent = (
    <StyledContentContainer>
      {plots && plots.length > 0 ? (
        <>
          {plots.map((plot, index) => (
            <StyledContentDiv key={index}>
              <PlotComponent data={plot.data} layout={plot.layout} hasResizing={true} />
              <SecondaryButton
                text="Download plot"
                style={{ width: "auto", alignSelf: "flex-start" }}
                onClick={() => {
                  handleDownloadPlot(plot);
                }}
              />
            </StyledContentDiv>
          ))}
          <PlotDownloadSettings
            isOpen={isDownloadModalOpen}
            onClose={closeDownloadModal}
            data={selectedPlot.data}
            layout={selectedPlot.layout}
          />
        </>
      ) : (
        <SectionTitle baseComponent={"h4"} description={"No plot available for this step."} />
      )}
    </StyledContentContainer>
  );

  const singleTableComponent = (table: Table) => (
    <StyledContentDiv>
      <DataTable data={table.table} />
      <CSVButton
        data={table.table}
        style={{ width: "auto", alignSelf: "flex-end", marginTop: theme.spacing.buttonGap }}
      />
    </StyledContentDiv>
  );

  const tableComponent = (
    <StyledContentContainer>
      {tableData && tableData.length > 0 ? (
        <SwitchCard
          components={tableData.map((table) => ({
            value: singleTableComponent(table),
            name: table.name,
          }))}
        />
      ) : (
        <SectionTitle baseComponent={"h4"} description={"No data table available for this step."} />
      )}
    </StyledContentContainer>
  );

  const otherComponent = <SwitchCard components={[{ name: "🚧", value: dummyTextComponent1 }]} />;

  const listEditorComponent = (
    <ListEditor
      onFormSubmit={onFormSubmit}
      runName={runName}
      handleStepSelection={handleStepSelection}
      runData={runData}
    />
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <StyledNavbar
        showRunInformation={true}
        title={runName}
        memoryUsage={runData.memory_usage}
        onNavigateHome={() => void navigate("/")}
        onOpenSettings={() => void navigate("/")}
        onOpenHelp={() => void navigate("/")}
      />

      <StyledCardRow>
        <StyledFlexColumn>
          <StyledListSwitchCard
            components={[
              { name: "List", value: listEditorComponent },
              { name: "Node", value: dummyTextComponent1 },
            ]}
            hasCardTitle={false}
            styleProps={{
              display: "flex",
              flexDirection: "column",
              height: "100%",
            }}
          />
        </StyledFlexColumn>
        <StyledFlexColumn style={{ flex: 1 }}>
          <StyledCol>
            <SwitchCard
              components={[
                { name: "Plots", value: plotComponent },
                { name: "Tables", value: tableComponent },
                { name: "Other Output", value: otherComponent },
              ]}
              hasCardTitle={false}
            />
          </StyledCol>
          <FooterText>{randomMessage}</FooterText>
        </StyledFlexColumn>
      </StyledCardRow>
    </div>
  );
};
