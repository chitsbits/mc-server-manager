import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'

function createData(name, port, dateCreated, numPlayers, status) {
  return { name, port, dateCreated, numPlayers, status }
}

const rows = [
  createData('1.16 main', 25565, '01/01/2024', 4, 'Online'),
  createData('manhunt', 25566, '01/01/2024', 4, 'Offline'),
]

export default function Servers() {
  return (
    <TableContainer sx={{ margin: '20px' }} component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Server Name</TableCell>
            <TableCell align="right">Port</TableCell>
            <TableCell align="right">Date Created</TableCell>
            <TableCell align="right"># Players</TableCell>
            <TableCell align="right">Status</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow
              key={row.name}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {row.name}
              </TableCell>
              <TableCell align="right">{row.port}</TableCell>
              <TableCell align="right">{row.dateCreated}</TableCell>
              <TableCell align="right">{row.numPlayers}</TableCell>
              <TableCell align="right">{row.status}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
