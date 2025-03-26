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


export const RunsTable: React.FC<RunsTableProps> = ({runs, setRuns}) => {

  const removeTag = (runName: string, tagToRemove: string) => {
    setRuns((prevRuns) =>
      prevRuns.map((run) =>
        run.run_name === runName
          ? { ...run, tags: run.run_tags.filter((tag) => tag !== tagToRemove) }
          : run
      )
    )
  }

  const toggleFavorite = (runName: string) => {
    const updated = runs.map((run) =>
      run.run_name === runName ? { ...run, favorite: !run.favourite_status } : run
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
        .sort((a, b) => (b.favourite_status ? 1 : 0) - (a.favourite_status ? 1 : 0)) // Favoriten oben
        .map((run) => (
        
            
        <TableRow key={run.run_name}>
          <TableCol 
            width="50px" 
            onClick={() => toggleFavorite(run.run_name)}
            style={{ cursor: "pointer"}}
            >            
            <Icon
              icon="starFill"
              style={{
                height: "15px",
                fill: run.favourite_status ? "gold" : "none",
              }}
            />
          </TableCol>
          <TableCol width="200px">{run.run_name}</TableCol>
          <TableCol width="150px">{run.modification_date}</TableCol>
          <TableCol>
            <TagList>
            {run.run_tags.map((tag, i) => (
                <Tag key={i}>
                    {tag}
                    <Icon 
                      icon="close"
                      color="gray"
                      onClick={() => removeTag(run.run_name, tag)}
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
