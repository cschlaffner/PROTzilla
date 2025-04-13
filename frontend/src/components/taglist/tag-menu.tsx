import { TagList } from "./taglist.tsx";
import { Form } from "../forms/form";
import { SearchInputField } from "../input-fields/search-input-field";
import React, { useEffect } from "react";
import { styled } from "styled-components";
import { spacing } from "../../theme";
import { callApi, Run } from "../../utils";

const StyledModalChild = styled.div`
  padding: ${spacing("small")};
`;

export interface tagMenuProps {
  selectedRun: Run;
  handleAddTag: (tag: string) => void;
  handleDeleteTag: (tag: string) => void;
}

export const TagMenu: React.FC<tagMenuProps> = ({
  selectedRun,
  handleAddTag,
  handleDeleteTag,
}) => {
  const [existingTags, setExistingTags] = React.useState<string[]>([]);
  const [searchTermTags, setSearchTermTags] = React.useState<string>("");

  const fetchData = async () => {
    const data = await callApi("run_information/");
    if (data) {
      setExistingTags(data[1]);
    }
  };

  useEffect(() => {
    void fetchData();
  }, []);

  const addableTags = existingTags.filter(
    (tag) => !selectedRun.run_tags.includes(tag),
  );
  const filteredAddableTags = addableTags.filter((tag) =>
    tag.toLocaleLowerCase().includes(searchTermTags.toLocaleLowerCase()),
  );

  const onHandleAddTag = async (tag: string) => {
    handleAddTag(tag);
    void fetchData();
  };

  return (
    <div>
      <TagList
        runName={selectedRun.run_name}
        tags={selectedRun.run_tags}
        icon="close"
        handleTag={handleDeleteTag}
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
              props: {
                label: "Add a new tag:",
              },
            },
          ],
        }}
        onChange={(data) => {
          void onHandleAddTag(data.tag as string);
        }}
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
          handleTag={onHandleAddTag}
        />
      </StyledModalChild>
    </div>
  );
};
