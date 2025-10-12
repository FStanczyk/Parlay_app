import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  CircularProgress,
  Alert,
  Button,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import ShuffleIcon from '@mui/icons-material/Shuffle';
import { useNavigate } from 'react-router-dom';
import { betEventsApi } from '../services/betEventsService';
import { BetEvent } from '../types/interfaces';
import { APP_NAME } from '../constants';
import BetEventPanel from '../components/BetEventPanel';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:600px)');
  const [betEvents, setBetEvents] = useState<BetEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBetEvents = async () => {
      try {
        setLoading(true);
        const events = await betEventsApi.getFiltered(); // sport_id = 1
        setBetEvents(events);
        console.log('Fetched bet events:', events);
      } catch (err) {
        console.error('Error fetching bet events:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch bet events');
      } finally {
        setLoading(false);
      }
    };

    fetchBetEvents();
  }, []);

  const handleBetClick = (betEvent: BetEvent) => {
    console.log('Bet clicked for event:', betEvent);
    // Navigate to betting page or open betting modal
    navigate('/dashboard');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress sx={{ color: 'text.primary' }} />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {!loading && !error && (
        <Box>
          <Typography variant="h4" component="h2" gutterBottom sx={{ color: 'text.primary', mb: 4, fontWeight: 600 }}>
            Make your parlay
          </Typography>
          
          <Grid container spacing={isMobile ? 1.5 : 3}>
            {betEvents.map((betEvent) => (
              <Grid item xs={12} md={6} lg={4} key={betEvent.id}>
                <BetEventPanel
                  betEvent={betEvent}
                />
              </Grid>
            ))}
          </Grid>

          {/* Generate Button */}
          {betEvents.length > 0 && (
            <Box textAlign="center" mt={4}>
              <Button
                variant="contained"
                size="large"
                endIcon={<ShuffleIcon />}
                sx={{
                  color: 'text.primary',
                  fontWeight: 600,
                  backgroundColor: '#ffffff',
                  borderRadius: '50px',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  }
                }}
              >
                Generate
              </Button>
            </Box>
          )}

          {betEvents.length === 0 && (
            <Box textAlign="center" py={8}>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                No betting events available at the moment
              </Typography>
            </Box>
          )}
        </Box>
      )}
    </Container>
  );
};

export default Home;
