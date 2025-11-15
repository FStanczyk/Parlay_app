import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  useMediaQuery,
  useTheme,
  Divider,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ScheduleIcon from '@mui/icons-material/Schedule';
import { BetEvent } from '../types/interfaces';

interface ParlaySummaryProps {
  betEvents: BetEvent[];
}

const ParlaySummary: React.FC<ParlaySummaryProps> = ({ betEvents }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:600px)');

  // Calculate summary data from bet events
  const calculateSummary = () => {
    if (!betEvents || betEvents.length === 0) {
      return {
        totalOdds: 0,
        minOdds: 0,
        maxOdds: 0,
        firstEventTime: null,
        lastEventTime: null,
      };
    }

    // Calculate total odds (multiply all odds together)
    const totalOdds = betEvents.reduce((acc, event) => acc * event.odds, 1);
    
    // Find min and max odds
    const odds = betEvents.map(event => event.odds);
    const minOdds = Math.min(...odds);
    const maxOdds = Math.max(...odds);

    // Find first and last event times
    const gameTimes = betEvents
      .filter(event => event.game?.datetime)
      .map(event => new Date(event.game!.datetime))
      .sort((a, b) => a.getTime() - b.getTime());

    const firstEventTime = gameTimes.length > 0 ? gameTimes[0] : null;
    const lastEventTime = gameTimes.length > 0 ? gameTimes[gameTimes.length - 1] : null;

    return {
      totalOdds,
      minOdds,
      maxOdds,
      firstEventTime,
      lastEventTime,
    };
  };

  const formatDateTime = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const summary = calculateSummary();

  return (
    <Card sx={{ marginBottom: 0, width: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        {/* Horizontal Layout */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
          {/* Left: Odds Info */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, fontSize: '0.7rem', mb: 0.25 }}>
                Total Odds
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 700, fontSize: '1.1rem' }}>
                {summary.totalOdds.toFixed(2)}
              </Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, fontSize: '0.7rem', mb: 0.25 }}>
                Min/Max
              </Typography>
              <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 600, fontSize: '0.8rem' }}>
                {summary.minOdds.toFixed(2)} - {summary.maxOdds.toFixed(2)}
              </Typography>
            </Box>
          </Box>

          {/* Right: Schedule */}
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 0.75
          }}>
            <ScheduleIcon sx={{ color: 'text.secondary', fontSize: '0.9rem' }} />
            <Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.1 }}>
                <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 500, fontSize: '0.75rem' }}>
                  First Event: {summary.firstEventTime ? formatDateTime(summary.firstEventTime) : 'N/A'}
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 500, fontSize: '0.75rem' }}>
                  Last Event: {summary.lastEventTime ? formatDateTime(summary.lastEventTime) : 'N/A'}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ParlaySummary;