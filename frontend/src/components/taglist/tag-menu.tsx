import { characterLimits, spacing, useTheme } from "@protzilla/theme";
import { callApi, Run } from "@protzilla/utils";
import React, { useCallback, useEffect } from "react";
import { styled } from "styled-components";

import { TagList } from "./taglist.tsx";
import { Form } from "../forms/form";
import { SearchInputField } from "../input-fields/search-input-field";
import { useNotification } from "../notification-center";

const StyledModalChild = styled.div`
  padding: ${spacing("small")};
`;

export interface TagMenuProps {
  selectedRun: Run;
  setSelectedRun: React.Dispatch<React.SetStateAction<Run>>;
  handleAddTag: (tag: string) => void;
  handleDeleteTag: (tag: string) => void;
}

export const TagMenu: React.FC<TagMenuProps> = ({
  setSelectedRun,
  selectedRun,
  handleAddTag,
  handleDeleteTag,
}) => {
  const notify = useNotification();

  const [existingTags, setExistingTags] = React.useState<string[]>([]);
  const [searchTermTags, setSearchTermTags] = React.useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      const response = await callApi("run_information/");
      if (response.success) {
        setExistingTags(response.data[1]);
      } else {
        notify({
          type: "error",
          message: "Error fetching existing tags",
          title: "Error",
        });
      }
    };

    void fetchData();
  }, [notify]);

  let addableTags: string[] = [];
  let filteredAddableTags: string[] = [];

  if (selectedRun.creation_date !== "Loading...") {
    addableTags = existingTags.filter((tag) => !selectedRun.run_tags.includes(tag));
    filteredAddableTags = addableTags.filter((tag) =>
      tag.toLocaleLowerCase().includes(searchTermTags.toLocaleLowerCase()),
    );
  }

  const theme = useTheme();

  const onHandleAddTag = useCallback(
    (tag: string) => {
      handleAddTag(tag);
      setSelectedRun((prevRun) => ({
        ...prevRun,
        run_tags: [...prevRun.run_tags, tag],
      }));
    },
    [handleAddTag, setSelectedRun],
  );

  const onHandleDeleteTag = (tag: string) => {
    handleDeleteTag(tag);
    setSelectedRun((prevRun) => ({
      ...prevRun,
      run_tags: prevRun.run_tags.filter((t) => t != tag),
    }));
  };

  return (
    <div>
      <TagList
        runName={selectedRun.run_name}
        tags={selectedRun.run_tags}
        icon="close"
        handleTag={onHandleDeleteTag}
      />
      <Form
        formData={{
          label: "",
          isAutoSubmit: false,
          hasChangeIndicator: false,
          input_fields: [
            {
              type: "text",
              name: "tag",
              label: "Add a new tag:",
              characterLimit: characterLimits("tag")({ theme }) as number,
              isVisible: true,
              value: "",
              placeholder: "",
            },
          ],
        }}
        onChange={useCallback(
          (data) => {
            onHandleAddTag(data.tag as string);
          },
          [onHandleAddTag],
        )}
      ></Form>
      <SearchInputField
        label="Or choose from existing tags:"
        style={{ padding: "0", gap: "0" }}
        value={searchTermTags}
        onChange={(e) => {
          setSearchTermTags(e);
        }}
        placeholder="Search existing tags"
      />
      <StyledModalChild>
        <TagList
          runName={selectedRun.run_name}
          tags={filteredAddableTags}
          icon="add"
          handleTag={(tag: string) => {
            onHandleAddTag(tag);
          }}
        />
      </StyledModalChild>
    </div>
  );
};
