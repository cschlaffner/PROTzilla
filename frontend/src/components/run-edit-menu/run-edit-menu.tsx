import { defaultPalette, size, spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters, formatDate, Run } from "@protzilla/utils";
import { forwardRef, useEffect, useState } from "react";
import { styled } from "styled-components";

import { RunEditMenuProps } from "./run-edit-menu.props.ts";
import { Form } from "../forms/form";
import { IconButton } from "../icon";
import { Modal } from "../modal";
import { useNotification } from "../notification-center";
import { SectionTitle } from "../section-title";
import { TagMenu } from "../taglist/tag-menu.tsx";
import { Text } from "../text";

const StyledModal = styled(Modal)`
  width: ${size("inputFieldsMaxWidth")};
`;

const Row = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${spacing("small")};
  align-items: center;
  padding-bottom: ${spacing("verySmall")};
`;

const TagMenuWrapper = styled.div`
  display: flex;
  flex-direction: column;
  padding-top: ${spacing("small")};
  gap: ${spacing("small")};
`;

export const RunEditMenu = forwardRef<HTMLDivElement, RunEditMenuProps>(
  (
    {
      runName,
      onChangeRunName,
      handleAddTag,
      handleDeleteTag,
      handleToggleFavourite,
      isOpen,
      onClose,
    },
    ref,
  ) => {
    const notify = useNotification();

    const [selectedRun, setSelectedRun] = useState<Run>({
      run_name: runName,
      creation_date: "Loading...",
      modification_date: "Loading...",
      memory_mode: "Loading...",
      run_steps: [],
      favourite_status: false,
      run_tags: [],
    });

    useEffect(() => {
      if (!runName) {
        return;
      }
      const fetchRunInformation = async () => {
        const response = await callApi("run_information/");
        if (response.success) {
          const run = response.data[0].find((run: Run) => run.run_name === runName);
          if (!run) {
            throw new Error(`Run with name "${runName}" not found`);
          }
          setSelectedRun(run);
        } else {
          notify({
            type: "error",
            message: "Error fetching run information",
            title: "Error",
          });
        }
      };

      void fetchRunInformation();
    }, [runName, notify]);

    const handleNameChange = async (newName: string) => {
      const response = await callApiWithParameters("update_run_name/", {
        run_name: selectedRun.run_name,
        new_run_name: newName,
      });
      if (!response?.success) {
        notify({
          title: "Run name update failed",
          message: response.message,
          type: "error",
        });
        throw new Error("Failed to update run name");
      } else {
        notify({
          title: "Run name updated",
          message: `Run name changed from ${selectedRun.run_name} to ${newName}`,
          type: "success",
        });

        selectedRun.run_name = newName;
        selectedRun.modification_date = new Date().toLocaleString("en-US");
        onChangeRunName(newName);
      }
    };

    const toggleFavorite = () => {
      handleToggleFavourite();
      setSelectedRun((prevRun) => ({
        ...prevRun,
        favourite_status: !prevRun.favourite_status,
      }));
    };

    return (
      <div ref={ref} id={"run-edit-menu"}>
        <StyledModal title={"Edit run information"} isOpen={isOpen} onClose={onClose}>
          <Row>
            <SectionTitle baseComponent={"h6"} title={"Favourited: "} />
            <IconButton
              icon={"starFill"}
              style={{
                fill: selectedRun.favourite_status ? defaultPalette.primary : "",
              }}
              onClick={() => {
                toggleFavorite();
              }}
            />
          </Row>
          <Row>
            <SectionTitle baseComponent={"h6"} title={"Date created: "} />
            <Text>{formatDate(selectedRun.creation_date)}</Text>
          </Row>
          <Row>
            <SectionTitle baseComponent={"h6"} title={"Date last modified: "} />
            <Text>{formatDate(selectedRun.modification_date)}</Text>
          </Row>
          <Row>
            <SectionTitle baseComponent={"h6"} title={"Memory mode: "} />
            <Text>{selectedRun.memory_mode}</Text>
          </Row>
          <Form
            formData={{
              label: "",
              isAutoSubmit: false,
              hasChangeIndicator: false,
              input_fields: [
                {
                  type: "text",
                  name: "run_name",
                  label: "Enter a new name:",
                  placeholder: selectedRun.run_name,
                  value: selectedRun.run_name,
                  isVisible: true,
                },
              ],
            }}
            onChange={(data) => {
              void handleNameChange(data.run_name as string);
            }}
          />
          <TagMenuWrapper>
            <SectionTitle baseComponent={"h6"} title={"Current tags: "} />
            <TagMenu
              setSelectedRun={setSelectedRun}
              selectedRun={selectedRun}
              handleAddTag={(tag) => {
                handleAddTag(tag);
              }}
              handleDeleteTag={(tag) => {
                handleDeleteTag(tag);
              }}
            />
          </TagMenuWrapper>
        </StyledModal>
      </div>
    );
  },
);

RunEditMenu.displayName = "RunEditMenu";
