import { useNotification } from "@protzilla/app";
import { DeleteModal, Form, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

const MultimerStructureTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const MultimerStructureList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

interface MultimerStructureProps {
  entry_id: string;
  uniprot_ids: string;
  date_modified: string;
  model_used: string;
  handleDelete?: () => void;
}

const MultimerStructureContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-left: ${spacing("listIndentation")};
  padding-top: ${spacing("verySmall")};
  padding-bottom: ${spacing("verySmall")};
`;

const MultimerStructureInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  width: 90%;
`;

const MultimerStructureEntry = ({
  entry_id,
  uniprot_ids,
  date_modified,
  model_used,
  handleDelete,
}: MultimerStructureProps) => {
  return (
    <MultimerStructureContainer>
      <MultimerStructureInfo>
        <SectionTitle baseComponent={"h6"} title={entry_id} />
        <Text
          text={
            "Protein IDs: " +
            uniprot_ids +
            " |  last modified " +
            date_modified +
            "  |  " +
            model_used
          }
        />
      </MultimerStructureInfo>
      <SecondaryButton icon={"trash"} isCautious={true} onPress={handleDelete} />
    </MultimerStructureContainer>
  );
};

export const MultimerStructureUpload = () => {
  const notify = useNotification();
  const [multimerStructureList, setMultimerStructureList] = useState<MultimerStructureProps[]>([]);
  const [isDeleteModalOpen, openDeleteModal, closeDeleteModal] = useToggleableState(false);
  const [selectedMultimerStructure, setSelectedMultimerStructure] = useState<string>("");

  const fetchMultimerStructures = async () => {
    const multimerStructures = await callApi("get_multimer_structure");
    if (multimerStructures) {
      setMultimerStructureList(multimerStructures);
    }
  };

  useEffect(() => {
    void fetchMultimerStructures();
  }, []);

  const handleAddMultimerStructure = async (
    entry_id: string,
    uniprot_ids: string,
    model_used: string,
    fasta_file: string,
    cif_file: string,
    confidence_file: string,
    full_data_file: string,
    job_request_file: string,
  ) => {
    const response = await callApiWithParameters("upload_multimer_structure", {
      entry_id: entry_id,
      uniprot_ids: uniprot_ids,
      model_used: model_used,
      fasta_file: fasta_file,
      cif_file: cif_file,
      confidence_file: confidence_file,
      full_data_file: full_data_file,
      job_request_file: job_request_file,
    });
    if (response?.success) {
      notify({
        title: "Predicted multimer structure upload",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Predicted multimer structure upload failed",
        message: response.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchMultimerStructures();
  };

  const onDeleteMultimerStructure = (entry_id: string) => {
    openDeleteModal();
    setSelectedMultimerStructure(entry_id);
  };

  const handleDeleteMultimerStructure = async (entry_id: string) => {
    const response = await callApiWithParameters("delete_multimer_structure", {
      entry_id: entry_id,
    });
    if (response?.success) {
      notify({
        title: "Multimer structure deleted",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Multimer structure deletion failed",
        message: response?.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchMultimerStructures();
    closeDeleteModal();
  };
  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Add a new multimer structure prediction"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={
          "Upload new multimer structure predictions and delete previously uploaded structures here."
        }
        style={{ paddingBottom: "8px" }}
      />

      <Form
        formData={{
          label: "",
          labelSubmitButton: "Upload Structure",
          isAutoSubmit: false,
          hasChangeIndicator: false,
          input_fields: [
            {
              type: "text",
              name: "entry_id",
              label: "Entry ID (required):",
              isVisible: true,
            },
            {
              type: "info-field",
              name: "entry_id_info",
              label: "The entry ID should be a unique name given to the uploaded prediction.",
              isVisible: true,
            },
            {
              type: "text",
              name: "uniprot_ids",
              label: "Protein IDs of all proteins used in the sequence (required):",
              isVisible: true,
            },
            {
              type: "info-field",
              name: "uniprot_ids_info",
              label:
                "Please provide the list of Protein IDs separated by a comma e.g.: P68871, P69905, Q5VSL9",
              isVisible: true,
            },
            {
              type: "text",
              name: "model_used",
              label: "AlphaFold Model used to predict the structure (required)",
              isVisible: true,
            },
            {
              type: "file",
              name: "fasta_file",
              label: "Sequences FASTA file (required):",
              isVisible: true,
              accept: ".fasta, .fa",
            },
            {
              type: "file",
              name: "cif_file",
              label: "CIF file (required):",
              isVisible: true,
              accept: ".cif",
            },
            {
              type: "file",
              name: "confidence_file",
              label: "Confidence summary JSON file (required):",
              isVisible: true,
              accept: ".json",
            },
            {
              type: "file",
              name: "full_data_file",
              label: "Full data json file (required):",
              isVisible: true,
              accept: ".json",
            },
            {
              type: "file",
              name: "job_request_file",
              label: "Job request json file (required):",
              isVisible: true,
              accept: ".json",
            },
          ],
        }}
        onChange={(data) => {
          void handleAddMultimerStructure(
            data.entry_id as string,
            data.uniprot_ids as string,
            data.model_used as string,
            data.fasta_file as string,
            data.cif_file as string,
            data.confidence_file as string,
            data.full_data_file as string,
            data.job_request_file as string,
          );
        }}
      />
      <MultimerStructureTitle
        baseComponent={"h2"}
        title={"Available Predicted Multimer Structures"}
      />
      {multimerStructureList.length === 0 ? (
        <Text
          text={
            "No predicted multimer structures uploaded yet. Use the form above to upload the FASTA sequences, the CIF file, and confidence and full data files. " +
            "Provide the Entry ID, the contained Protein Ids and the Alphafold version, then click 'Upload Structure'. You can also upload multimer predictions directly " +
            "in a run with the multimer structure upload step under Importing."
          }
        />
      ) : (
        <MultimerStructureList>
          {multimerStructureList.map((ps) => (
            <MultimerStructureEntry
              key={ps.entry_id}
              entry_id={ps.entry_id}
              uniprot_ids={ps.uniprot_ids}
              date_modified={ps.date_modified}
              model_used={ps.model_used}
              handleDelete={() => {
                onDeleteMultimerStructure(ps.entry_id);
              }}
            />
          ))}
        </MultimerStructureList>
      )}
      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={() => void handleDeleteMultimerStructure(selectedMultimerStructure)}
        title={
          `The uploaded multimer structure prediction with the entry ID ` +
          `"${selectedMultimerStructure}" will permanently be deleted. Would you like to proceed?`
        }
      />
    </div>
  );
};
