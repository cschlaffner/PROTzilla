import { useState } from "react"
import { color } from "../../theme"
import { Button, SecondaryButton } from "../button"
import { Icon } from "../icon"
import { RunsTableProps } from "./runs-table.props"
import styled from "styled-components"

const TableContainer = styled.div`
  display: flex;
  flex-direction: column;
`

const TableRow = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
  background-color: #fff;

  &:nth-of-type(even) {
    background-color: ${color("protzillaLightBlue")};
  }
`

const TableCol = styled.div<{ width?: string }>`
  flex: ${({ width }) => (width ? "0 0 " + width : "1")};
  text-align: left;
  padding: 8px 8px;
`

const TableHeader = styled(TableRow)`
  font-weight: bold;
  border-bottom: 2px solid #ccc;
  padding-bottom: 4px;
`

const TagList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
`

const Tag = styled.span`
  background-color: ${color("protzillaDarkBlue")};
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
`


export const RunsTable: React.FC<RunsTableProps> = ({}) => {
  // Dummy-Daten
  const initialData = [
    {
      id: 1,
      runName: "Jannes",
      edited: "yesterday",
      tags: ["HBSC"],
      favorite: false,
    },
    {
      id: 2,
      runName: "Leonardo",
      edited: "21.03.2025",
      tags: ["04", "Tag 1"],
      favorite: false,
    },
    {
      id: 3,
      runName: "Lennotani",
      edited: "17.02.2025",
      tags: ["DasIstEinTag"],
      favorite: false,
    },
  ]

  const removeTag = (runId: number, tagToRemove: string) => {
    setRuns((prevRuns) =>
      prevRuns.map((run) =>
        run.id === runId
          ? { ...run, tags: run.tags.filter((tag) => tag !== tagToRemove) }
          : run
      )
    )
  }
  

  // Local state
  const [runs, setRuns] = useState(initialData)

  const toggleFavorite = (id: number) => {
    const updated = runs.map((run) =>
      run.id === id ? { ...run, favorite: !run.favorite } : run
    )
    setRuns(updated)
  }

  

  return (
    <TableContainer>
      <TableHeader>
        <TableCol width="50px">Favorite</TableCol>
        <TableCol width="200px">Run Name</TableCol>
        <TableCol width="150px">Last edited</TableCol>
        <TableCol>Tags</TableCol>
        <TableCol width="80px">Actions</TableCol>
        <TableCol width="100px">Continue</TableCol>
      </TableHeader>

      {[...runs]
        .sort((a, b) => (b.favorite ? 1 : 0) - (a.favorite ? 1 : 0)) // Favoriten oben
        .map((run) => (
        
            
        <TableRow key={run.id}>
          <TableCol 
            width="50px" 
            onClick={() => toggleFavorite(run.id)}
            style={{ cursor: "pointer"}}
            >            
            <Icon
              icon="starFill"
              style={{
                height: "15px",
                fill: run.favorite ? "gold" : "none",
              }}
            />
          </TableCol>
          <TableCol width="200px">{run.runName}</TableCol>
          <TableCol width="150px">{run.edited}</TableCol>
          <TableCol>
            <TagList>
            {run.tags.map((tag, i) => (
                <Tag key={i}>
                    {tag}
                    <Icon 
                      icon="close"
                      color="gray"
                      onClick={() => removeTag(run.id, tag)}
                      aria-label={`Remove tag ${tag}`}
                      style={{
                        height: "15px",
                      }}
                    />
                </Tag>
            ))}
            </TagList>
          </TableCol>
          <TableCol width="80px">
            <SecondaryButton isSmall={true} isShy={true}>
              <Icon icon={"edit"} style={{ height: "15px" }} />
            </SecondaryButton>
          </TableCol>
          <TableCol width="100px">
            <SecondaryButton isSmall={true}>Continue</SecondaryButton>
          </TableCol>
        </TableRow>
      ))}
    </TableContainer>
  )
}
