import { SectionTitle } from "../../../section-title";
import { Text } from "../../../text";
import { TextInputField } from "../../../input-fields/text-input-field";
import { FileInputField } from "../../../input-fields/file-input-field";
import { SecondaryButton } from "../../../button";
import { styled } from "styled-components";
import { spacing } from "../../../../theme";
import { useEffect, useState } from "react";
import { callApi } from "../../../../utils";

const SettingsDiv = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const DatabasesTitle = styled(SectionTitle)`
  padding-top: ${spacing("large")};
  padding-bottom: ${spacing("small")};
`;

const DatabaseList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
  overflow-y: auto;
  max-height: 28vh;
`;

interface DatabaseEntryProps {
  num_proteins: number;
  date: string;
  filesize: number;
  cols: string[];
  name: string;
}

const DatabaseEntryContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
`;

const DatabaseEntryInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-content: center;
  flex-direction: column;
  gap: 2px;
  width: 80%;
`;

const ColumnContainer = styled.div`
  display: flex;
  flex-direction: row;
  gap: 4px;
`;

const DatabaseEntry = ({
  num_proteins,
  date,
  filesize,
  cols,
  name,
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
      return size * 0.001 + " KB";
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
      <SecondaryButton text={"Delete"} isCautious={true} onPress={() => {}} />
    </DatabaseEntryContainer>
  );
};

export const DatabaseSettings = ({}) => {
  const [databaseList, setDatabaseList] = useState<DatabaseEntryProps[]>([]);

  const fetchDatabases = async () => {
    const databases = await callApi("databases");
    if (databases) {
      setDatabaseList(databases);
    } else {
      console.error("Failed to fetch databases");
    }
  };

  useEffect(() => {
    void fetchDatabases();
  }, []);

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
      <SettingsDiv>
        <TextInputField
          onChange={() => {}}
          label={"Name for new database (required):"}
        />
        <FileInputField
          onChange={() => {}}
          label={"Database file (required):"}
        />
        <Text
          text={
            "TODO CLICK FIELD Copy file without verification and protein count"
          }
        />
        <SecondaryButton
          text={"Add database"}
          onPress={() => {}}
          style={{ width: "30%" }}
        />
      </SettingsDiv>
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
          />
        ))}
        <DatabaseEntry
          num_proteins={20000}
          date={"1.1.25"}
          filesize={3}
          cols={[
            "Entry",
            "Entry Name",
            "Protein names",
            "Gene Names",
            "Organism",
            "Length",
          ]}
          name={"human_reviewed"}
        />
        <DatabaseEntry
          num_proteins={20000}
          date={"1.1.25"}
          filesize={3}
          cols={[
            "Entry",
            "Entry Name",
            "Protein names",
            "Gene Names",
            "Organism",
            "Length",
          ]}
          name={"human_reviewed"}
        />
        <DatabaseEntry
          num_proteins={20000}
          date={"1.1.25"}
          filesize={3}
          cols={[
            "Entry",
            "Entry Name",
            "Protein names",
            "Gene Names",
            "Organism",
            "Length",
          ]}
          name={"human_reviewed"}
        />
        <DatabaseEntry
          num_proteins={20000}
          date={"1.1.25"}
          filesize={3}
          cols={[
            "Entry",
            "Entry Name",
            "Protein names",
            "Gene Names",
            "Organism",
            "Length",
          ]}
          name={"human_reviewed"}
        />
        <DatabaseEntry
          num_proteins={20000}
          date={"1.1.25"}
          filesize={3}
          cols={[
            "Entry",
            "Entry Name",
            "Protein names",
            "Gene Names",
            "Organism",
            "Length",
          ]}
          name={"human_reviewed"}
        />
      </DatabaseList>
    </div>
  );
};
