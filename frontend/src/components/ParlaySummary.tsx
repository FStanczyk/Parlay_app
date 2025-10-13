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

const ParlaySummary: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width:600px)');

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
                23.4
              </Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, fontSize: '0.7rem', mb: 0.25 }}>
                Min/Max
              </Typography>
              <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 600, fontSize: '0.8rem' }}>
                1.5 - 1.87
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
                  First Event: Oct 13, 17:30
                </Typography>
                <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 500, fontSize: '0.75rem' }}>
                  Last Event:  Oct 13, 21:45
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