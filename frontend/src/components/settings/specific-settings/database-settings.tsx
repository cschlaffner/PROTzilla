import { useEffect, useState } from "react";
import { styled } from "styled-components";

import { Form, SecondaryButton, Text } from "../../../components";
import { SectionTitle } from "../../section-title";
import { spacing } from "../../../theme";
import { callApi, callApiWithParameters } from "../../../utils";

const DatabasesTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const DatabaseList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing("verySmall")};
`;

interface DatabaseEntryProps {
  num_proteins: number;
  date: string;
  filesize: number;
  cols: string[];
  name: string;
  handleDelete?: () => void;
}

const DatabaseEntryContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-left: ${spacing("listIndentation")};
  padding-top: ${spacing("verySmall")};
  padding-bottom: ${spacing("verySmall")};
`;

const DatabaseEntryInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  width: 90%;
`;

const ColumnContainer = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${spacing("verySmall")};
`;

const DatabaseEntry = ({
  num_proteins,
  date,
  filesize,
  cols,
  name,
  handleDelete,
}: DatabaseEntryProps) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "2-digit",
    });
  };

  const formatSize = (size: number) => {
    if (size < 1000000) {
      return (size * 0.001).toFixed(2) + " KB";
    } else {
      return (size * 0.000001).toFixed(2) + " MB";
    }
  };

  const formatProteins = (num_proteins: number) => {
    if (num_proteins > 1000) {
      return num_proteins
        .toString()
        .split(/(?=(?:\d{3})+(?!\d))/)
        .join(",");
    }
    return num_proteins.toString();
  };

  return (
    <DatabaseEntryContainer>
      <DatabaseEntryInfo>
        <SectionTitle baseComponent={"h6"} title={name} />
        <Text
          text={
            formatProteins(num_proteins) +
            " proteins  |  Added on " +
            formatDate(date) +
            "  |  " +
            formatSize(filesize)
          }
        />
        <ColumnContainer>
          <Text text={"Columns: "} />
          <Text text={cols.join(", ")} />
        </ColumnContainer>
      </DatabaseEntryInfo>
      <SecondaryButton
        icon={"trash"}
        isCautious={true}
        onPress={handleDelete}
      />
    </DatabaseEntryContainer>
  );
};

export const DatabaseSettings = () => {
  const [databaseList, setDatabaseList] = useState<DatabaseEntryProps[]>([]);

  const fetchDatabases = async () => {
    const databases = await callApi("databases");
    if (databases) {
      setDatabaseList(databases);
    }
  };

  useEffect(() => {
    void fetchDatabases();
  }, []);

  const handleAddDatabase = async (
    databaseName: string,
    databaseFile: string,
    shouldVerify: boolean,
  ) => {
    await callApiWithParameters("upload_database", {
      name: databaseName,
      just_copy: shouldVerify ? "True" : "False",
      file: databaseFile,
    });
    void fetchDatabases();
  };

  const handleDeleteDatabase = async (name: string) => {
    await callApiWithParameters("delete_database", {
      name: name,
    });
    void fetchDatabases();
  };

  return (
    <div>
      <SectionTitle
        baseComponent={"h2"}
        title={"Add a new database"}
        style={{ paddingBottom: "4px" }}
      />
      <SectionTitle
        baseComponent={"h6"}
        description={
          "To download a database, go to uniprot.org/uniprotkb. A tutorial is available in the PROTzilla documentation."
        }
        style={{ paddingBottom: "8px" }}
      />
      <Form
        formData={{
          label: "",
          isAutoSubmit: false,
          input_fields: [
            {
              type: "text",
              name: "database_name",
              props: {
                label: "Name for new database (required):",
              },
            },
            {
              type: "file",
              name: "database_file",
              props: {
                label: "Database file (required):",
              },
            },
            {
              type: "single-checkbox",
              name: "verification_checkbox",
              props: {
                label: "Verification",
                text: "Copy file without verification and protein count.",
              },
            },
          ],
        }}
        onChange={(data) => {
          void handleAddDatabase(
            data.database_name as string,
            data.database_file as string,
            data.verification_checkbox === "true",
          );
        }}
      />
      <DatabasesTitle
        baseComponent={"h2"}
        title={"Available Uniprot Databases"}
      />
      <DatabaseList>
        {databaseList.map((db) => (
          <DatabaseEntry
            key={db.name}
            num_proteins={db.num_proteins}
            date={db.date}
            filesize={db.filesize}
            cols={db.cols}
            name={db.name}
            handleDelete={() => void handleDeleteDatabase(db.name)}
          />
        ))}
      </DatabaseList>
    </div>
  );
};
