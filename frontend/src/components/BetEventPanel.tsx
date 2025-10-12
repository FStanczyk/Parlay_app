import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import LockIcon from '@mui/icons-material/Lock';
import { BetEvent } from '../types/interfaces';

interface BetEventPanelProps {
  betEvent: BetEvent;
}

const BetEventPanel: React.FC<BetEventPanelProps> = ({
  betEvent,
}) => {
  const [isLocked, setIsLocked] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:600px)');

  const handleLockToggle = () => {
    setIsLocked(!isLocked);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card
      sx={{
        borderRadius: 3,
        boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.12)',
        background: 'rgba(216 179 243 / 0.2)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        transition: 'all 0.3s ease-in-out',
        position: 'relative',
        '&:hover': {
          boxShadow: '0px 12px 40px rgba(0, 0, 0, 0.18)',
        },
      }}
    >
      {/* Lock Icon - Top Right Corner */}
      <IconButton
        onClick={handleLockToggle}
        sx={{
          position: 'absolute',
          top: isMobile ? 16 : 24,
          right: isMobile ? 16 : 24,
          color: isLocked ? '#ffffff' : 'text.secondary',
          backgroundColor: isLocked ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255)',
          backdropFilter: 'blur(10px)',
          borderRadius: '50%',
          width: 32,
          height: 32,
          '&:hover': {
            backgroundColor: isLocked ? 'rgba(0, 0, 0, 0.9)' : 'rgba(255, 255, 255, 0.8)',
          }
        }}
        size="small"
      >
        {isLocked ? <LockIcon fontSize="small" /> : <LockOpenIcon fontSize="small" />}
      </IconButton>

      <CardContent sx={{ p: isMobile ? 2 : 3 }}>
        {/* Main Content Layout - Two Rows */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: isMobile ? 1 : 2 }}>
          {/* Top Row - Team names and Event */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box sx={{ flex: 1 }}>
              {/* Home team - Away team (bold at top left) */}
              <Typography variant="body1" component="h3" sx={{ fontWeight: 700, color: 'text.primary', mb: isMobile ? 0 : 0.5 }}>
                {betEvent.home_team} - {betEvent.away_team}
              </Typography>
              
              {/* Event name (below in secondary color) */}
              <Typography variant="body1" color="text.secondary">
                {betEvent.event}
              </Typography>
            </Box>
          </Box>

          {/* Bottom Row - Odds and League/Date */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {/* Left side - Odds */}
            <Box>
              <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 500 }}>
                {betEvent.odds}
              </Typography>
            </Box>

            {/* Right side - League and Date */}
            <Box sx={{ textAlign: 'right' }}>
              {/* League name (top line) */}
              <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, fontSize: '0.75rem', lineHeight: 1.2 }}>
                {betEvent.league?.name || `League ${betEvent.league_id}`}
              </Typography>
              
              {/* Date and time (bottom line) */}
              <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, fontSize: '0.75rem', lineHeight: 1.2 }}>
                {formatDate(betEvent.datetime)}
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BetEventPanel;
