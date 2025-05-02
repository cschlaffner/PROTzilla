import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { styled, useTheme } from "styled-components";

import { useToggleableState } from "../../hooks";
import { color, defaultPalette } from "../../theme";
import { callApiWithParameters, Run } from "../../utils";
import { SecondaryButton } from "../button";
import { Icon } from "../icon";
import { DeleteModal } from "../modal";
import { RunsTableProps } from "./runs-table.props";
import { TagList } from "../taglist";
import { formatDate } from "../../utils/format-date.ts";
import { RunEditMenu } from "../run-edit-menu/run-edit-menu.tsx";

const TableContainer = styled.div`
  display: flex;
  flex-direction: column;
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

const TableRow = styled.div<{ preSelected?: boolean }>`
  display: flex;
  justify-content: space-between;
  width: 100%;
  background-color: #fff;

  &:nth-of-type(even) {
    background-color: ${color("protzillaLightBlue")};
  }

  ${({ preSelected, theme }) =>
    preSelected
      ? `
          border: ${theme.borders.defaultStrength} solid ${theme.colors.primary};
          border-radius: ${theme.borders.defaultRadius};
        `
      : `
          border: none;
        `}
`;

const TableCol = styled.div<{ width?: string }>`
  flex: ${({ width }) => (width ? "0 0 " + width : "1")};
  text-align: left;
  padding: 8px 8px;
  min-width: 50px;
`;

const TableHeader = styled(TableRow)`
  font-weight: bold;
  border-bottom: 2px solid #ccc;
  padding-bottom: 4px;
`;
const StyledList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`;

export const RunsTable: React.FC<RunsTableProps> = ({
  runs,
  filteredRuns,
  setRuns,
  openTagModal,
  setSelectedRun,
}) => {
  const navigate = useNavigate();
  const theme = useTheme();

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isRunEditModalOpen, openRunEditModal, closeRunEditModal] =
    useToggleableState(false);
  const [preSelectedRun, setPreSelectedRun] = useState<string | null>(null);
  const [actionRun, setActionRun] = useState<string>("");

  const handleDeleteTag = (tagToDelete: string, runName: string) => {
    void callApiWithParameters("delete_tag/", {
      run_name: runName,
      tag_name: tagToDelete,
    });
    setRuns((runs) =>
      runs.map((run) =>
        run.run_name === runName
          ? {
              ...run,
              run_tags: run.run_tags.filter((tag) => tag !== tagToDelete),
            }
          : run,
      ),
    );
  };

  const handleToggleFavourite = (runName: string) => {
    void callApiWithParameters("toggle_favourite/", {
      run_name: runName,
    });
    const updated = runs.map((run) =>
      run.run_name === runName
        ? { ...run, favourite_status: !run.favourite_status }
        : run,
    );
    setRuns(updated);
  };

  const handleDeleteRun = (runName: string) => {
    void callApiWithParameters("delete_run/", { run_name: runName });
    const updated = runs.filter((run) => run.run_name !== runName);
    setIsDeleteModalOpen(false);
    setRuns(updated);
  };

  const handleContinueRun = (runName: string) => {
    void callApiWithParameters("continue_run/", { run_name: runName }).then(
      () => {
        void navigate("/run", { state: { runName } });
      },
    );
  };

  const handleRenameRun = (newName: string) => {
    const updated = runs.map((run) =>
      run.run_name === actionRun ? { ...run, run_name: newName } : run,
    );
    setRuns(updated);
  };

  const handleModal = (run: Run) => {
    setSelectedRun(run);
    openTagModal(true);
  };

  const handleDeleteModal = (runName: string) => {
    setActionRun(runName);
    setIsDeleteModalOpen(true);
  };

  const handleRunEditModal = (runName: string) => {
    setActionRun(runName);
    openRunEditModal();
  };

  return (
    <TableContainer>
      <TableHeader>
        <TableCol width={theme.sizes.smallCellWidth}>Favorite</TableCol>
        <TableCol width={theme.sizes.largeCellWidth}>Run Name</TableCol>
        <TableCol width={theme.sizes.mediumCellWidth}>Last edited</TableCol>
        <TableCol>Tags</TableCol>
        <TableCol width={theme.sizes.mediumCellWidth}>Actions</TableCol>
      </TableHeader>

      {[...filteredRuns]
        // Favourites on top
        .sort(
          (a, b) => (b.favourite_status ? 1 : 0) - (a.favourite_status ? 1 : 0),
        )
        .map((run) => (
          <TableRow
            key={run.run_name}
            onDoubleClick={() => {
              handleContinueRun(run.run_name);
            }}
            onClick={() => {
              if (preSelectedRun === run.run_name) {
                handleContinueRun(run.run_name);
              } else {
                setPreSelectedRun(run.run_name);
              }
            }}
            preSelected={run.run_name === preSelectedRun}
            style={{
              cursor: "pointer",
            }}
          >
            <TableCol
              width={theme.sizes.smallCellWidth}
              onClick={(e) => {
                e.stopPropagation();
                handleToggleFavourite(run.run_name);
              }}
              style={{ cursor: "pointer" }}
            >
              <Icon
                icon="starFill"
                style={{
                  height: "15px",
                  fill: run.favourite_status ? defaultPalette.primary : "none",
                }}
              />
            </TableCol>
            <TableCol width={theme.sizes.largeCellWidth}>
              {run.run_name}
            </TableCol>
            <TableCol width={theme.sizes.mediumCellWidth}>
              {formatDate(run.modification_date)}
            </TableCol>
            <TableCol>
              <StyledList>
                <TagList
                  runName={run.run_name}
                  tags={run.run_tags}
                  icon="close"
                  handleTag={handleDeleteTag}
                />
                <SecondaryButton
                  isSmall={true}
                  isShy={true}
                  onClick={(e) => {
                    handleModal(run);
                    e.stopPropagation();
                  }}
                >
                  <Icon
                    icon={"threeDots"}
                    style={{ height: "15px", fill: defaultPalette.primary }}
                  />
                </SecondaryButton>
              </StyledList>
            </TableCol>
            <TableCol width={theme.sizes.mediumCellWidth}>
              <SecondaryButton
                isSmall={true}
                isShy={true}
                onClick={(e) => {
                  handleRunEditModal(run.run_name);
                  e.stopPropagation();
                }}
              >
                <Icon icon={"edit"} style={{ height: "15px" }} />
              </SecondaryButton>
              <SecondaryButton
                isSmall={true}
                isShy={true}
                isCautious={true}
                onClick={(e) => {
                  handleDeleteModal(run.run_name);
                  e.stopPropagation();
                }}
              >
                <Icon icon={"trash"} style={{ height: "15px" }} />
              </SecondaryButton>
              <SecondaryButton
                isSmall={true}
                isShy={true}
                onClick={(e) => {
                  e.stopPropagation();
                  handleContinueRun(run.run_name);
                }}
              >
                <Icon icon={"play"} style={{ height: "15px" }} />
                Go!
              </SecondaryButton>
            </TableCol>
          </TableRow>
        ))}
      <DeleteModal
        title={`Delete run "${actionRun}"?`}
        isOpen={isDeleteModalOpen}
        onConfirm={() => {
          handleDeleteRun(actionRun);
        }}
        onClose={() => {
          setIsDeleteModalOpen(false);
        }}
      />
      {isRunEditModalOpen && (
        <RunEditMenu
          key={actionRun} // Ensures a new instance for each run
          runName={actionRun}
          onChangeRunName={(newRunName) => {
            handleRenameRun(newRunName);
          }}
          isOpen={isRunEditModalOpen}
          onClose={closeRunEditModal}
        />
      )}
    </TableContainer>
  );
};
