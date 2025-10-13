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
  Fade,
  Slide,
} from '@mui/material';
import ShuffleIcon from '@mui/icons-material/Shuffle';
import { useNavigate } from 'react-router-dom';
import { betEventsApi } from '../services/betEventsService';
import { BetEvent } from '../types/interfaces';
import { APP_NAME } from '../constants';
import BetEventPanel from '../components/BetEventPanel';
import Filters, { FilterValues } from '../components/Filters';
import ParlaySummary from '../components/ParlaySummary';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:600px)');
  const [betEvents, setBetEvents] = useState<BetEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lockedEventIds, setLockedEventIds] = useState<Set<number>>(new Set());
  const [filters, setFilters] = useState<FilterValues>({
    selectedSport: '',
    selectedLeague: '',
    minOdds: '',
    maxOdds: '',
    eventsNumber: '',
  });

  useEffect(() => {
    const fetchBetEvents = async () => {
      try {
        setLoading(true);
        // Use random selection with default limit of 10, or use eventsNumber from filters
        const limit = filters.eventsNumber ? parseInt(filters.eventsNumber) : 4;
        const events = await betEventsApi.getRandom(limit);
        setBetEvents(events);
        // Clear locked events when fetching new events (filter change)
        setLockedEventIds(new Set());
        console.log('Fetched random bet events:', events);
      } catch (err) {
        console.error('Error fetching bet events:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch bet events');
      } finally {
        setLoading(false);
      }
    };

    fetchBetEvents();
  }, [filters.eventsNumber]);

  const handleBetClick = (betEvent: BetEvent) => {
    console.log('Bet clicked for event:', betEvent);
    // Navigate to betting page or open betting modal
    navigate('/dashboard');
  };

  const handleLockToggle = (eventId: number) => {
    setLockedEventIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const handleGenerateClick = async () => {
    try {
      setGenerating(true);
      const limit = filters.eventsNumber ? parseInt(filters.eventsNumber) : 4;
      
      // Calculate how many new events we need (total - locked events)
      const lockedEvents = betEvents.filter(event => lockedEventIds.has(event.id));
      const newEventsNeeded = limit - lockedEvents.length;
      
      let newEvents: BetEvent[] = [];
      
      if (newEventsNeeded > 0) {
        // Get all currently displayed event IDs to exclude them
        const currentEventIds = betEvents.map(event => event.id);
        
        // Get new random events for the remaining slots, excluding current ones
        newEvents = await betEventsApi.getRandom(newEventsNeeded, undefined, undefined, currentEventIds);
      }
      
      // Combine locked events with new events
      const combinedEvents = [...lockedEvents, ...newEvents];
      
      setBetEvents(combinedEvents);
      console.log('Generated new random bet events:', combinedEvents);
    } catch (err) {
      console.error('Error generating bet events:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate bet events');
    } finally {
      setGenerating(false);
    }
  };

  const handleFiltersChange = (newFilters: FilterValues) => {
    setFilters(newFilters);
    console.log('Filters updated:', newFilters);
    // The useEffect will automatically refetch when eventsNumber changes
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
          
          {/* Filters Component */}
          <Filters onFiltersChange={handleFiltersChange} />
          
          {/* Generate Button */}
          {betEvents.length > 0 && (
            <Box textAlign="center" mb={4}>
              <Button
                variant="contained"
                size="large"
                endIcon={<ShuffleIcon />}
                onClick={handleGenerateClick}
                disabled={generating}
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
                  },
                  '&:disabled': {
                    backgroundColor: 'rgba(255, 255, 255, 0.5)',
                    color: 'rgba(0, 0, 0, 0.5)',
                  }
                }}
              >
                Generate
              </Button>
            </Box>
          )}
          {/* ParlaySummary - Above the grid, width matches one column */}
          <Box sx={{ mb: 4 }}>
            <ParlaySummary />
          </Box>
          
          <Box position="relative">
            <Grid container spacing={isMobile ? 1.5 : 3}>
              {betEvents.map((betEvent, index) => (
                <Grid item xs={12} md={6} lg={4} key={betEvent.id}>
                  <Fade in={!generating} timeout={300} style={{ transitionDelay: `${index * 50}ms` }}>
                    <div>
                      <BetEventPanel
                        betEvent={betEvent}
                        isLocked={lockedEventIds.has(betEvent.id)}
                        onLockToggle={handleLockToggle}
                      />
                    </div>
                  </Fade>
                </Grid>
              ))}
            </Grid>
            
            {/* Subtle overlay during generation */}
            {generating && (
              <Fade in={generating} timeout={200}>
                <Box
                  position="absolute"
                  top={0}
                  left={0}
                  right={0}
                  bottom={0}
                  bgcolor="rgba(255, 255, 255, 0.1)"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  sx={{ pointerEvents: 'none' }}
                >
                  <CircularProgress size={40} sx={{ color: 'text.primary' }} />
                </Box>
              </Fade>
            )}
          </Box>

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
