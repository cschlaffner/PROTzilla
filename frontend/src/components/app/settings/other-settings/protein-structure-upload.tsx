import { useNotification } from "@protzilla/app";
import { DeleteModal, Form, SecondaryButton, SectionTitle, Text } from "@protzilla/core";
import { useToggleableState } from "@protzilla/hooks";
import { spacing } from "@protzilla/theme";
import { callApi, callApiWithParameters } from "@protzilla/utils";
import { useEffect, useState } from "react";
import { styled } from "styled-components";

const ProteinStructureTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const ProtStructureList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

interface ProtStructureProps {
  entry_id: string;
  uniprot_id: string;
  date_modified: string;
  gene: string;
  af_version: string;
  handleDelete?: () => void;
}

const ProtStructureContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-left: ${spacing("listIndentation")};
  padding-top: ${spacing("verySmall")};
  padding-bottom: ${spacing("verySmall")};
`;

const ProtStructureInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  width: 90%;
`;

const ProtStructureEntry = ({
  entry_id,
  uniprot_id,
  date_modified,
  gene,
  af_version,
  handleDelete,
}: ProtStructureProps) => {
  return (
    <ProtStructureContainer>
      <ProtStructureInfo>
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
            af_version
          }
        />
      </ProtStructureInfo>
      <SecondaryButton icon={"trash"} isCautious={true} onPress={handleDelete} />
    </ProtStructureContainer>
  );
};

export const ProteinStructureUpload = () => {
  const notify = useNotification();
  const [protStructureList, setProtStructureList] = useState<ProtStructureProps[]>([]);
  const [isDeleteModalOpen, openDeleteModal, closeDeleteModal] = useToggleableState(false);
  const [selectedProtStructure, setSelectedProtStructure] = useState<string>("");

  const fetchProtStructures = async () => {
    const protStructures = await callApi("get_prot_structure");
    if (protStructures) {
      setProtStructureList(protStructures);
    }
  };

  useEffect(() => {
    void fetchProtStructures();
  }, []);

  const handleAddProteinStructure = async (
    uniprot_id: string,
    entry_id: string,
    af_version: string,
    gene: string,
    cif_file: string,
    confidence: string,
    pae: string,
    fasta_file: string,
  ) => {
    const response = await callApiWithParameters("upload_prot_structure", {
      uniprot_id: uniprot_id,
      entry_id: entry_id,
      af_version: af_version,
      gene: gene,
      cif_file: cif_file,
      confidence: confidence,
      pae: pae,
      fasta_file: fasta_file,
    });
    if (response?.success) {
      notify({
        title: "Predicted protein structure upload",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Predicted protein structure upload failed",
        message: response.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchProtStructures();
  };

  const onDeleteProtStructure = (entry_id: string) => {
    openDeleteModal();
    setSelectedProtStructure(entry_id);
  };

  const handleDeleteProtStructure = async (entry_id: string) => {
    const response = await callApiWithParameters("delete_prot_structure", {
      entry_id: entry_id,
    });
    if (response?.success) {
      notify({
        title: "Protein structure deleted",
        message: response.message as string,
        type: "success",
        isClosingAutomatically: true,
      });
    } else {
      notify({
        title: "Protein structure deletion failed",
        message: response?.message ?? "Unknown error",
        type: "error",
        isClosingAutomatically: true,
      });
    }
    void fetchProtStructures();
    closeDeleteModal();
  };

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Add a new protein structure prediction"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={
          "Upload new protein structure predictions and delete previously uploaded structures here."
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
              type: "text",
              name: "af_version",
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
          void handleAddProteinStructure(
            data.uniprot_id as string,
            data.entry_id as string,
            data.af_version as string,
            data.gene as string,
            data.cif_file as string,
            data.confidence_file as string,
            data.pae_file as string,
            data.fasta_file as string,
          );
        }}
      />
      <ProteinStructureTitle
        baseComponent={"h2"}
        title={"Available Predicted Protein Structures"}
      />
      {protStructureList.length === 0 ? (
        <Text
          text={
            "No predicted protein structures uploaded yet. Use the form above to upload a CIF file, confidence and PAE JSON files, and a FASTA sequence. " +
            "Provide Uniprot ID, Entry ID, Alphafold version and gene name, then click 'Upload Structure'. Else use the step in the workflow under 'Importing' " +
            "to directly fetch Alphafold predictions from the Alphafold Database."
          }
        />
      ) : (
        <ProtStructureList>
          {protStructureList.map((ps) => (
            <ProtStructureEntry
              key={ps.entry_id}
              entry_id={ps.entry_id}
              uniprot_id={ps.uniprot_id}
              date_modified={ps.date_modified}
              gene={ps.gene}
              af_version={ps.af_version}
              handleDelete={() => {
                onDeleteProtStructure(ps.entry_id);
              }}
            />
          ))}
        </ProtStructureList>
      )}
      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={() => void handleDeleteProtStructure(selectedProtStructure)}
        title={
          `The uploaded protein structure prediction with the entryID ` +
          `"${selectedProtStructure}" will permanently be deleted. Would you like to proceed?`
        }
      />
    </div>
  );
};
