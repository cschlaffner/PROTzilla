import { useNotification } from "@protzilla/app";
import { DeleteModal, Form, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

const CrosslinkDefaultTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const CrosslinkDefaultList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

interface CrosslinkDefaultProps {
  cl_name: string;
  cl_length: number;
  cl_upper_deviation: number;
  cl_lower_deviation: number;
  handleDelete?: () => void;
}

type ApiCrosslinkDefaults = Record<
  string,
  {
    cl_length: number;
    cl_upper_deviation: number;
    cl_lower_deviation: number;
  }
>;

const CrosslinkDefaultContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-left: ${spacing("listIndentation")};
  padding-top: ${spacing("verySmall")};
  padding-bottom: ${spacing("verySmall")};
`;

const CrosslinkDefaultInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  width: 90%;
`;

const CrosslinkDefaultEntry = ({
  cl_name,
  cl_length,
  cl_upper_deviation,
  cl_lower_deviation,
  handleDelete,
}: CrosslinkDefaultProps) => {
  return (
    <CrosslinkDefaultContainer>
      <CrosslinkDefaultInfo>
        <SectionTitle baseComponent={"h6"} title={cl_name} />
        <Text
          text={
            `length: ${String(cl_length)} | ` +
            `accepted upper deviation: ${String(cl_upper_deviation)} | ` +
            `accepted lower deviation: ${String(cl_lower_deviation)}`
          }
        />
      </CrosslinkDefaultInfo>
      <SecondaryButton icon={"trash"} isCautious={true} onPress={handleDelete} />
    </CrosslinkDefaultContainer>
  );
};

export const CrosslinkDefaultUpload = () => {
  const notify = useNotification();
  const [crosslinkDefaultList, setCrosslinkDefaultList] = useState<CrosslinkDefaultProps[]>([]);
  const [isDeleteModalOpen, openDeleteModal, closeDeleteModal] = useToggleableState(false);
  const [selectedCrosslinkDefault, setSelectedCrosslinkDefault] = useState<string>("");

  const fetchCrosslinkDefaults = async () => {
    const crosslinkDefaults = (await callApi("get_cl_defaults")) as ApiCrosslinkDefaults | null;

    if (crosslinkDefaults) {
      const transformedList: CrosslinkDefaultProps[] = Object.entries(crosslinkDefaults).map(
        ([name, properties]) => ({
          cl_name: name,
          cl_length: properties.cl_length,
          cl_upper_deviation: properties.cl_upper_deviation,
          cl_lower_deviation: properties.cl_lower_deviation,
        }),
      );
      setCrosslinkDefaultList(transformedList);
    }
  };

  useEffect(() => {
    void fetchCrosslinkDefaults();
  }, []);

  const handleAddCrosslinkDefault = async (
    cl_name: string,
    cl_length: number,
    cl_upper_deviation: number,
    cl_lower_deviation: number,
  ) => {
    const response = await callApiWithParameters("update_cl_default", {
      cl_name: cl_name,
      cl_length: cl_length,
      cl_upper_deviation: cl_upper_deviation,
      cl_lower_deviation: cl_lower_deviation,
    });
    if (response?.success) {
      notify({
        title: "Crosslink default update",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Crosslink default update failed",
        message: response.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchCrosslinkDefaults();
  };

  const onDeleteCrosslinkDefault = (cl_name: string) => {
    openDeleteModal();
    setSelectedCrosslinkDefault(cl_name);
  };

  const handleDeleteCrosslinkDefault = async (cl_name: string) => {
    const response = await callApiWithParameters("delete_cl_default", {
      cl_name: cl_name,
    });
    if (response?.success) {
      notify({
        title: "Cross Link default deleted",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Cross Link default deletion failed",
        message: response?.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchCrosslinkDefaults();
    closeDeleteModal();
  };

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Add a default for a specific Cross-Link"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={"Add new default, update and delete them here."}
        style={{ paddingBottom: "8px" }}
      />

      <Form
        formData={{
          label: "",
          labelSubmitButton: "Add defaults",
          isAutoSubmit: false,
          hasChangeIndicator: false,
          input_fields: [
            {
              type: "text",
              name: "cl_name",
              label: "Name of the Cross-Link",
              isVisible: true,
            },
            {
              type: "number",
              name: "cl_length",
              label: "Length of the specified Cross-Link:",
              isVisible: true,
            },
            {
              type: "number",
              name: "cl_upper_deviation",
              label: "Upper deviation of the specified Cross-Link:",
              isVisible: true,
            },
            {
              type: "number",
              name: "cl_lower_deviation",
              label: "Lower deviation of the specified Cross-Link:",
              isVisible: true,
            },
          ],
        }}
        onChange={(data) => {
          void handleAddCrosslinkDefault(
            data.cl_name as string,
            data.cl_length as number,
            data.cl_upper_deviation as number,
            data.cl_lower_deviation as number,
          );
        }}
      />
      <CrosslinkDefaultTitle baseComponent={"h2"} title={"Cross-Link Defaults"} />
      {crosslinkDefaultList.length === 0 ? (
        <Text text={"No default values for any cross-links yet."} />
      ) : (
        <CrosslinkDefaultList>
          {crosslinkDefaultList.map((ps) => (
            <CrosslinkDefaultEntry
              key={ps.cl_name}
              cl_name={ps.cl_name}
              cl_length={ps.cl_length}
              cl_upper_deviation={ps.cl_upper_deviation}
              cl_lower_deviation={ps.cl_lower_deviation}
              handleDelete={() => {
                onDeleteCrosslinkDefault(ps.cl_name);
              }}
            />
          ))}
        </CrosslinkDefaultList>
      )}
      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={() => void handleDeleteCrosslinkDefault(selectedCrosslinkDefault)}
        title={
          `Defaults for  ` +
          `"${selectedCrosslinkDefault}" will permanently be deleted. Would you like to proceed?`
        }
      />
    </div>
  );
};
