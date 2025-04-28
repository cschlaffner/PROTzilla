import { forwardRef, useEffect, useState } from "react";
import { styled } from "styled-components";

import { RunEditMenuProps } from "./run-edit-menu.props.ts";
import { defaultPalette, size, spacing } from "../../theme";
import { callApi, callApiWithParameters, Run } from "../../utils";
import { formatDate } from "../../utils/format-date.ts";
import { Form } from "../forms/form";
import { IconButton } from "../icon";
import { Modal } from "../modal";
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
  ({ runName, onChangeRunName, isOpen, onClose }, ref) => {
    const [selectedRun, setSelectedRun] = useState<Run>({
      run_name: runName,
      creation_date: "Loading...",
      modification_date: "Loading...",
      memory_mode: "Loading...",
      run_steps: [],
      favourite_status: false,
      run_tags: ["Loading", "..."],
    });

    useEffect(() => {
      const fetchRunInformation = async () => {
        const data = await callApi("run_information/");
        if (data) {
          const run = data[0].find((run: Run) => run.run_name === runName);
        if (!run) {
          throw new Error(`Run with name "${runName}" not found`);
        }
        setSelectedRun(run);
        }
      };

      void fetchRunInformation();
    }, [runName]);

    const handleNameChange = async (newName: string) => {
      await callApiWithParameters("update_run_name/", {
        run_name: runName,
        new_run_name: newName,
      });
      selectedRun.run_name = newName;
      onChangeRunName(newName);
    };

    const handleAddTag = async (tag: string) => {
      await callApiWithParameters("add_tag/", {
        run_name: selectedRun.run_name,
        tag_name: tag,
      });
    };

    const handleDeleteTag = async (tagToDelete: string) => {
      await callApiWithParameters("delete_tag/", {
        run_name: selectedRun.run_name,
        tag_name: tagToDelete,
      });
    };

    const toggleFavorite = async () => {
      await callApiWithParameters("toggle_favourite/", {
        run_name: selectedRun.run_name,
      });
      setSelectedRun((prevRun) => ({
        ...prevRun,
        favourite_status: !prevRun.favourite_status,
      }));
    };

    console.log("selectedRun", selectedRun);

    return (
      <div ref={ref} id={"run-edit-menu"}>
        <StyledModal
          title={"Edit run information"}
          isOpen={isOpen}
          onClose={onClose}
        >
          <Row>
            <SectionTitle baseComponent={"h6"} title={"Favourited: "} />
            <IconButton
              icon={"starFill"}
              style={{
                fill: selectedRun.favourite_status
                  ? defaultPalette.primary
                  : "",
              }}
              onClick={() => {
                void toggleFavorite();
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
              hasChangeIndicator: true,
              input_fields: [
                {
                  type: "text",
                  name: "run_name",
                  props: {
                    label: "Enter a new name:",
                    placeholder: selectedRun.run_name,
                    value: selectedRun.run_name,
                  },
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
              handleAddTag={(tag) => void handleAddTag(tag)}
              handleDeleteTag={(tag) => void handleDeleteTag(tag)}
            />
          </TagMenuWrapper>
        </StyledModal>
      </div>
    );
  },
);

RunEditMenu.displayName = "RunEditMenu";
