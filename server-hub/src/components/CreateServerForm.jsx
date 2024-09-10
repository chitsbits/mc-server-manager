import {
  Button,
  Checkbox,
  Container,
  FormControl,
  FormControlLabel,
  FormGroup,
  Grid2,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import axios from 'axios';
import { useState } from 'react';

const BASE_URL = process.env.REACT_APP_API_GATEWAY_URL;

const CreateServerForm = () => {
  // Define state for form input fields
  const [serverName, setServerName] = useState('My Server');
  const [motd, setMotd] = useState('');
  const [maxPlayers, setMaxPlayers] = useState(0);
  const [difficulty, setDifficulty] = useState('');
  const [gameMode, setGameMode] = useState('');
  const [persistence, setPersistence] = useState(true);
  const [port, setPort] = useState(30000);

  const [status, setStatus] = useState('');
  const [disableBtn, setDisableBtn] = useState(false);

  // Function to handle form submission
  const handleCreateServer = async (e) => {
    e.preventDefault(); // Prevent default form submission

    // Prepare server data
    const serverData = {
      serverName: serverName || 'Minecraft Server',
      minecraftServer: {
        eula: true,
        gameMode: gameMode || 'creative',
        difficulty: difficulty || 'peaceful',
        motd: motd || 'A sample MOTD',
        serviceType: 'NodePort',
        nodePort: port || 30000,
      },
      persistence: {
        dataDir: {
          enabled: persistence || true,
        },
      },
    };

    console.log('Server data:', serverData);

    try {
      // Send a POST request to create the server
      const response = await axios.post(
        `${BASE_URL}/servers/create`,
        serverData
      );
      setDisableBtn(true);

      if (response.status === 200) {
        setStatus('Server created.');
        setDisableBtn(false);
      } else {
        setStatus('Failed to initiate server creation.');
        setDisableBtn(false);
      }
    } catch (error) {
      console.error('Error creating server:', error);
      setStatus('Error creating server.');
      setDisableBtn(false);
    }
  };

  // State for validation errors
  const [errors, setErrors] = useState({
    serverName: '',
    port: '',
  });

  // Helper to validate fields
  const validate = () => {
    let tempErrors = { ...errors };

    // Validate server name (e.g., must not be empty)
    tempErrors.serverName = serverName ? '' : 'Server name is required';

    // Validate port (e.g., must be between 30000 and 32767)
    if (!port) {
      tempErrors.port = 'Port is required';
    } else if (isNaN(port) || port < 30000 || port > 32767) {
      tempErrors.port = 'Port must be a number between 30000 and 32767';
    } else {
      tempErrors.port = '';
    }

    setErrors(tempErrors);

    // Return true if there are no errors
    return Object.values(tempErrors).every((x) => x === '');
  };

  // Handle form submission
  const handleSubmit = (event) => {
    event.preventDefault(); // Prevent default form submission

    if (validate()) {
      // Submit form if valid
      handleCreateServer(event);
      console.log('Form submitted');
    } else {
      console.log('Form has errors');
    }
  };

  // // Function to listen for updates using SSE
  // const listenForUpdates = (serverId) => {
  //   const eventSource = new EventSource(
  //     `http://localhost:5000/events/${serverId}`
  //   );

  //   eventSource.onmessage = (event) => {
  //     const data = JSON.parse(event.data);
  //     console.log('Server update:', data);

  //     if (data.status === 'success') {
  //       setStatus(`Server ${serverId} created successfully!`);
  //       eventSource.close();
  //     } else if (data.status === 'failed') {
  //       setStatus(`Server ${serverId} creation failed.`);
  //       eventSource.close();
  //     }
  //   };

  //   eventSource.onerror = (err) => {
  //     console.error('EventSource error:', err);
  //     setStatus('Error with event updates.');
  //     eventSource.close();
  //   };
  // };

  return (
    <Container maxWidth="lg">
      <h1>Create a Minecraft Server</h1>

      <form onSubmit={handleSubmit}>
        <Grid2 container spacing={2}>
          <Grid2>
            <FormGroup>
              <TextField
                label="Server Name"
                variant="outlined"
                margin="normal"
                value={serverName}
                onChange={(e) => setServerName(e.target.value)}
                placeholder="Enter server name"
                error={!serverName} // Shows error state
                helperText={!serverName && 'Required'} // Shows error message
              />
              <TextField
                label="Max Players"
                variant="outlined"
                margin="normal"
                type="number"
                value={maxPlayers}
                onChange={(e) => setMaxPlayers(Number(e.target.value))}
                placeholder="20"
              />
              <TextField
                label="MOTD"
                variant="outlined"
                margin="normal"
                value={motd}
                onChange={(e) => setMotd(e.target.value)}
                placeholder="Server created thru FE"
              />

              <FormControlLabel
                control={
                  <Checkbox
                    defaultChecked
                    value={persistence}
                    onChange={(e) => setPersistence(Boolean(e.target.value))}
                  />
                }
                label="Persist server on stop"
              />
            </FormGroup>
          </Grid2>
          <Grid2>
            <FormGroup>
              <FormControl margin="normal">
                <InputLabel>Difficulty</InputLabel>
                <Select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  label="Difficutly"
                >
                  <MenuItem value={'peaceful'}>Peaceful</MenuItem>
                  <MenuItem value={'easy'}>Easy</MenuItem>
                  <MenuItem value={'normal'}>Normal</MenuItem>
                  <MenuItem value={'hard'}>Hard</MenuItem>
                </Select>
              </FormControl>

              <FormControl margin="normal">
                <InputLabel>Gamemode</InputLabel>
                <Select
                  value={gameMode}
                  onChange={(e) => setGameMode(e.target.value)}
                  label="Gamemode"
                >
                  <MenuItem value={'survival'}>Survival</MenuItem>
                  <MenuItem value={'creative'}>Creative</MenuItem>
                  <MenuItem value={'spectator'}>Spectator</MenuItem>
                </Select>
              </FormControl>

              <TextField
                label="Port"
                variant="outlined"
                margin="normal"
                value={port}
                type="number"
                onChange={(e) => setPort(Number(e.target.value))}
                placeholder="30000"
                error={port < 30000 || port > 32767} // Shows error state
                helperText={
                  (port < 30000 || port > 32767) &&
                  'Port must be between 30000 and 32767'
                } // Shows error message
              />
            </FormGroup>
          </Grid2>
        </Grid2>
        <Button
          variant="contained"
          type="submit"
          sx={{ mt: 2 }}
          disabled={
            disableBtn ||
            !serverName ||
            !port ||
            !!errors.serverName ||
            !!errors.port
          }
        >
          Create Server
        </Button>
      </form>
      {status && (
        <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
          {status}
        </Typography>
      )}
    </Container>
  );
};

export default CreateServerForm;
