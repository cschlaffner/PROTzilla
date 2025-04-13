import { forwardRef, useEffect, useState } from "react";
import { styled } from "styled-components";

import { RunEditMenuProps } from "./run-edit-menu.props.ts";
import { spacing } from "../../theme";
import { callApi, callApiWithParameters, Run } from "../../utils";
import { Card } from "../card";
import { Form } from "../forms/form";
import { SectionTitle } from "../section-title";
import { TagMenu } from "../taglist/tag-menu.tsx";
import { Text } from "../text";

const MenuWrapper = styled.div`
  position: absolute;
  top: ${spacing("navbarHeight")};
  left: 0;
`;

const StyledCard = styled(Card)`
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
  ({ runName, onChangeRunName }, ref) => {
    const [selectedRun, setSelectedRun] = useState<Run>({
      run_name: "",
      creation_date: "string",
      modification_date: "string",
      memory_mode: "string",
      run_steps: [],
      favourite_status: true,
      run_tags: ["notreal"],
    });

    const fetchRunInformation = async () => {
      const data = await callApi("run_information/");
      if (data) {
        const run: Run = data[0].find(
          (run: Run) => run.run_name === runName,
        ) as Run;
        setSelectedRun(run);
      }
    };

    useEffect(() => {
      void fetchRunInformation();
    });

    const handleNameChange = async (newName: string) => {
      await callApiWithParameters("update_run_name/", {
        run_name: runName,
        new_run_name: newName,
      });
      await fetchRunInformation();
      onChangeRunName(newName);
    };

    const handleAddTag = async (tag: string) => {
      await callApiWithParameters("add_tag/", {
        run_name: runName,
        tag_name: tag,
      });
      await fetchRunInformation();
    };

    const handleDeleteTag = async (tagToDelete: string) => {
      await callApiWithParameters("delete_tag/", {
        run_name: runName,
        tag_name: tagToDelete,
      });
      await fetchRunInformation();
    };

    return (
      <MenuWrapper ref={ref} id={"run-edit-menu"}>
        <StyledCard>
          <Row>
            <SectionTitle baseComponent={"h6"} title={"Date created: "} />
            <Text>{selectedRun.creation_date}</Text>
          </Row>
          <Row>
            <SectionTitle baseComponent={"h6"} title={"Date last modified: "} />
            <Text>{selectedRun.modification_date}</Text>
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
                  props: {
                    label: "Enter a new name:",
                    value: runName,
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
              handleAddTag={(tag) => void handleAddTag(tag)}
              handleDeleteTag={(tag) => void handleDeleteTag(tag)}
            />
          </TagMenuWrapper>
        </StyledCard>
      </MenuWrapper>
    );
  },
);

RunEditMenu.displayName = "RunEditMenu";
