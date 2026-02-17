import { useNotification } from "@protzilla/app";
import { DeleteModal, Form, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

const MonomerStructureTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const MonomerStructureList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

interface MonomerStructureProps {
  entry_id: string;
  uniprot_id: string;
  date_modified: string;
  gene: string;
  model_used: string;
  handleDelete?: () => void;
}

const MonomerStructureContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-left: ${spacing("listIndentation")};
  padding-top: ${spacing("verySmall")};
  padding-bottom: ${spacing("verySmall")};
`;

const MonomerStructureInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  width: 90%;
`;

const MonomerStructureEntry = ({
  entry_id,
  uniprot_id,
  date_modified,
  gene,
  model_used,
  handleDelete,
}: MonomerStructureProps) => {
  return (
    <MonomerStructureContainer>
      <MonomerStructureInfo>
        <SectionTitle baseComponent={"h6"} title={entry_id} />
        <Text
          text={
            "Uniprot Accession: " +
            uniprot_id +
            " |  Last Modified " +
            date_modified +
            "  |  " +
            gene +
            "  |  " +
            model_used
          }
        />
      </MonomerStructureInfo>
      <SecondaryButton icon={"trash"} isCautious={true} onPress={handleDelete} />
    </MonomerStructureContainer>
  );
};

export const MonomerStructureUpload = () => {
  const notify = useNotification();
  const [monomerStructureList, setMonomerStructureList] = useState<MonomerStructureProps[]>([]);
  const [isDeleteModalOpen, openDeleteModal, closeDeleteModal] = useToggleableState(false);
  const [selectedMonomerStructure, setSelectedMonomerStructure] = useState<string>("");

  const fetchMonomerStructures = async () => {
    const monomerStructures = await callApi("get_monomer_structure");
    if (monomerStructures) {
      setMonomerStructureList(monomerStructures);
    }
  };

  useEffect(() => {
    void fetchMonomerStructures();
  }, []);

  const handleAddMonomerStructure = async (
    uniprot_id: string,
    entry_id: string,
    model_used: string,
    gene: string,
    cif_file: string,
    confidence: string,
    pae: string,
    fasta_file: string,
  ) => {
    const response = await callApiWithParameters("upload_monomer_structure", {
      uniprot_id: uniprot_id,
      entry_id: entry_id,
      model_used: model_used,
      gene: gene,
      cif_file: cif_file,
      confidence: confidence,
      pae: pae,
      fasta_file: fasta_file,
    });
    if (response?.success) {
      notify({
        title: "Predicted monomer structure upload",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Predicted monomer structure upload failed",
        message: response.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchMonomerStructures();
  };

  const onDeleteMonomerStructure = (entry_id: string) => {
    openDeleteModal();
    setSelectedMonomerStructure(entry_id);
  };

  const handleDeleteMonomerStructure = async (entry_id: string) => {
    const response = await callApiWithParameters("delete_monomer_structure", {
      entry_id: entry_id,
    });
    if (response?.success) {
      notify({
        title: "Monomer structure deleted",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Monomer structure deletion failed",
        message: response?.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchMonomerStructures();
    closeDeleteModal();
  };

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Add a new monomer structure prediction"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={
          "Upload new monomer structure predictions and delete previously uploaded structures here."
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
              name: "uniprot_id",
              label: "Uniprot ID (required):",
              isVisible: true,
            },
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
              name: "model_used",
              label: "Alphafold Version Number (required):",
              isVisible: true,
            },
            {
              type: "text",
              name: "gene",
              label: "Gene Name (required):",
              isVisible: true,
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
              label: "Confidence JSON file (required):",
              isVisible: true,
              accept: ".json",
            },
            {
              type: "file",
              name: "pae_file",
              label: "Predicted Aligned Error JSON file (required):",
              isVisible: true,
              accept: ".json",
            },
            {
              type: "file",
              name: "fasta_file",
              label: "Sequence FASTA file (required):",
              isVisible: true,
              accept: ".fasta, .fa",
            },
          ],
        }}
        onChange={(data) => {
          void handleAddMonomerStructure(
            data.uniprot_id as string,
            data.entry_id as string,
            data.model_used as string,
            data.gene as string,
            data.cif_file as string,
            data.confidence_file as string,
            data.pae_file as string,
            data.fasta_file as string,
          );
        }}
      />
      <MonomerStructureTitle
        baseComponent={"h2"}
        title={"Available Predicted Monomer Structures"}
      />
      {monomerStructureList.length === 0 ? (
        <Text
          text={
            "No predicted monomer structures uploaded yet. Use the form above to upload a CIF file, confidence and PAE JSON files, and a FASTA sequence. " +
            "Provide Uniprot ID, Entry ID, Alphafold version and gene name, then click 'Upload Structure'. Else use the step in the workflow under 'Importing' " +
            "to directly fetch Alphafold predictions from the Alphafold Database."
          }
        />
      ) : (
        <MonomerStructureList>
          {monomerStructureList.map((ps) => (
            <MonomerStructureEntry
              key={ps.entry_id}
              entry_id={ps.entry_id}
              uniprot_id={ps.uniprot_id}
              date_modified={ps.date_modified}
              gene={ps.gene}
              model_used={ps.model_used}
              handleDelete={() => {
                onDeleteMonomerStructure(ps.entry_id);
              }}
            />
          ))}
        </MonomerStructureList>
      )}
      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={() => void handleDeleteMonomerStructure(selectedMonomerStructure)}
        title={
          `The uploaded monomer structure prediction with the entry ID ` +
          `"${selectedMonomerStructure}" will permanently be deleted. Would you like to proceed?`
        }
      />
    </div>
  );
};
