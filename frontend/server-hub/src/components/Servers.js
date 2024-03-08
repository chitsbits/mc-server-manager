
import * as React from 'react';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';
import Title from './Title';
import { Container, Grid, Paper } from '@mui/material';

function preventDefault(event) {
  event.preventDefault();
}

export default function Servers() {
  return (
    <React.Fragment>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
        {/* Recent Orders */}
        <Grid item xs={12}>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Title>ServerList</Title>
            <Typography component="p" variant="h4">
                $3,024.00
            </Typography>
            <Typography color="text.secondary" sx={{ flex: 1 }}>
                on 15 March, 2019
            </Typography>
            <div>
                <Link color="primary" href="#" onClick={preventDefault}>
                View balance
                </Link>
            </div>
            </Paper>
        </Grid>
        </Grid>
    </Container>
    </React.Fragment>
  );
}



