import { forwardRef, useEffect, useState } from "react";
import { styled } from "styled-components";

import { RunEditMenuProps } from "./run-edit-menu.props.ts";
import { spacing } from "../../theme";
import { callApi, callApiWithParameters, Run } from "../../utils";
import { formatDate } from "../../utils/format-date.ts";
import { Form } from "../forms/form";
import { SectionTitle } from "../section-title";
import { TagMenu } from "../taglist/tag-menu.tsx";
import { Text } from "../text";
import { Modal } from "../modal";

const StyledModal = styled(Modal)`
  width: 500px;
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
      creation_date: "",
      modification_date: "",
      memory_mode: "",
      run_steps: [],
      favourite_status: true,
      run_tags: [],
    });

    const fetchRunInformation = async () => {
      const data = await callApi("run_information/");
      if (data) {
        const run: Run = data[0].find(
          (run: Run) => run.run_name === selectedRun.run_name,
        ) as Run;
        console.log("run", run);
        setSelectedRun(run);
      }
    };

    useEffect(() => {
      void fetchRunInformation();
    }, []);

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

    return (
      <div ref={ref} id={"run-edit-menu"}>
        <StyledModal title={"Edit run"} isOpen={isOpen} onClose={onClose}>
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
              selectedRun={selectedRun}
              setSelectedRun={setSelectedRun}
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
