import AddIcon from '@mui/icons-material/Add';
import LoadingButton from '@mui/lab/LoadingButton';
import {
  Button,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid2,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import axios from 'axios';
import React, { useEffect, useState } from 'react';

const BASE_URL = process.env.REACT_APP_API_GATEWAY_URL;

export default function Servers() {
  const [serverList, setServerList] = useState([]);
  const [loadingState, setLoadingState] = useState({}); // To track the loading state of each server action

  const [openDialog, setOpenDialog] = useState(false);

  const handleClickOpen = () => {
    setOpenDialog(true);
  };

  const handleClose = () => {
    setOpenDialog(false);
  };

  useEffect(() => {
    const eventSource = new EventSource(`${BASE_URL}/servers/status/all`); // API Gateway URL

    eventSource.onmessage = (event) => {
      try {
        // The data in Server-Sent Events is prefixed with "data:", so we need to remove it
        console.log(event);
        const cleanData = event.data.replace(/^data:\s*/, ''); // Remove "data:" part
        console.log(cleanData);
        const parsedData = JSON.parse(cleanData);
        setServerList(parsedData);
        console.log(parsedData);
      } catch (error) {
        console.error('Error parsing data', error);
      }
    };

    // Clean up when the component unmounts
    return () => {
      eventSource.close();
    };
  }, []);

  // Helper to update loading state
  const setLoading = (serverId, action, isLoading) => {
    setLoadingState((prev) => ({
      ...prev,
      [serverId]: { ...prev[serverId], [action]: isLoading },
    }));
  };

  // Event handler for starting a server
  const handleStartServer = async (serverId) => {
    setLoading(serverId, 'start', true);
    try {
      await axios.post(`${BASE_URL}/servers/${serverId}/start`);
      console.log(`Server ${serverId} started successfully`);
    } catch (error) {
      console.error(`Error starting server ${serverId}:`, error);
    } finally {
      setLoading(serverId, 'start', false);
    }
  };

  // Event handler for stopping a server
  const handleStopServer = async (serverId) => {
    setLoading(serverId, 'stop', true);
    try {
      await axios.post(`${BASE_URL}/servers/${serverId}/stop`);
      console.log(`Server ${serverId} stopped successfully`);
    } catch (error) {
      console.error(`Error stopping server ${serverId}:`, error);
    } finally {
      setLoading(serverId, 'stop', false);
    }
  };

  // Event handler for deleting a server
  const handleDeleteServer = async (serverId) => {
    setLoading(serverId, 'delete', true);
    try {
      setServerList((prev) =>
        prev.filter((server) => server.server_id !== serverId)
      );

      await axios.delete(`${BASE_URL}/servers/${serverId}`);
      console.log(`Server ${serverId} deleted successfully`);
    } catch (error) {
      console.error(`Error deleting server ${serverId}:`, error);
    } finally {
      setLoading(serverId, 'delete', false);
    }
  };

  return (
    <React.Fragment>
      <Container sx={{ mt: 3 }} className="wrapper">
        <Grid2 container spacing={2}>
          <h1>Servers</h1>
          <Grid2 display="flex" alignItems="center">
            <Button
              href="/create-server"
              variant="contained"
              startIcon={<AddIcon />}
            >
              Add Server
            </Button>
          </Grid2>
        </Grid2>
        {JSON.stringify(serverList)}
        <TableContainer sx={{ mt: '10px' }} component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell>Server Name</TableCell>
                <TableCell align="right">Port</TableCell>
                <TableCell align="right">MOTD</TableCell>
                <TableCell align="right"># Players</TableCell>
                <TableCell align="right">Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {serverList.map((row) => (
                <TableRow
                  key={row.server_id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    {row.server_id}
                  </TableCell>
                  <TableCell align="right">{row.port}</TableCell>
                  <TableCell align="right">
                    {row.description && row.description}
                  </TableCell>
                  <TableCell align="right">
                    {row.players && `${row.players.online}/${row.players.max}`}
                  </TableCell>
                  <TableCell align="right">{row.status}</TableCell>

                  <TableCell align="right">
                    <LoadingButton
                      variant="contained"
                      color="primary"
                      onClick={() => handleStartServer(row.server_id)}
                      disabled={row.status === 'Running'}
                      loading={loadingState[row.server_id]?.start || false}
                    >
                      Start
                    </LoadingButton>
                    <LoadingButton
                      variant="contained"
                      color="secondary"
                      onClick={() => handleStopServer(row.server_id)}
                      disabled={row.status === 'Stopped'}
                      loading={loadingState[row.server_id]?.stop || false}
                      sx={{ ml: 1 }}
                    >
                      Stop
                    </LoadingButton>
                    <LoadingButton
                      variant="contained"
                      color="error"
                      onClick={() => handleClickOpen()}
                      disabled={row.status === 'Running'}
                      loading={loadingState[row.server_id]?.delete || false}
                      sx={{ ml: 1 }}
                    >
                      Delete
                    </LoadingButton>
                    <Dialog
                      open={openDialog}
                      onClose={handleClose}
                      aria-labelledby="alert-dialog-title"
                      aria-describedby="alert-dialog-description"
                    >
                      <DialogTitle id="alert-dialog-title">
                        {'Delete Server?'}
                      </DialogTitle>
                      <DialogContent>
                        <DialogContentText id="alert-dialog-description">
                          Are you sure you want to delete this server?
                        </DialogContentText>
                      </DialogContent>
                      <DialogActions>
                        <Button onClick={handleClose}>No</Button>
                        <Button
                          onClick={() => {
                            handleDeleteServer(row.server_id);
                            handleClose();
                          }}
                          autoFocus
                        >
                          Yes
                        </Button>
                      </DialogActions>
                    </Dialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>
    </React.Fragment>
  );
}
