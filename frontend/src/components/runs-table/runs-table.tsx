import {RunsTableProps} from "./runs-table.props"
import styled from "styled-components"

const TableContainer = styled.ul`
    list-style-type: none;
`
const TableRow = styled.li`
    display: flex;
    width: 500px;
    justify-content: space-between
`
const TableCol = styled.li`
    display: inline;

`

export const RunsTable: React.FC<RunsTableProps> = ({}) => {
    return(
        <div>
            <TableContainer>
                <TableRow>
                    <TableCol>Das ist ein Run Name</TableCol>
                    <TableCol>1</TableCol>
                    <TableCol>1</TableCol>
                </TableRow>
                
                <TableRow>
                    <TableCol>2</TableCol>
                    <TableCol>2</TableCol>
                    <TableCol>2</TableCol>
                </TableRow>

                <TableRow>
                    <TableCol>3</TableCol>
                    <TableCol>3</TableCol>
                    <TableCol>3</TableCol>
                </TableRow>
            </TableContainer>

        </div>
    )
}