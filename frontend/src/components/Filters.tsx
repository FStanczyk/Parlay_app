import React, { useState } from 'react';
import {
  Box,
  Grid,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Collapse,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

export interface FilterValues {
  selectedSport: string;
  selectedLeague: string;
  minOdds: string;
  maxOdds: string;
  eventsNumber: string;
}

interface FiltersProps {
  onFiltersChange: (filters: FilterValues) => void;
}

const Filters: React.FC<FiltersProps> = ({ onFiltersChange }) => {
  const [selectedSport, setSelectedSport] = useState<string>('');
  const [selectedLeague, setSelectedLeague] = useState<string>('');
  const [showMoreFilters, setShowMoreFilters] = useState(false);
  const [minOdds, setMinOdds] = useState<string>('');
  const [maxOdds, setMaxOdds] = useState<string>('');
  const [eventsNumber, setEventsNumber] = useState<string>('');

  // Function to update parent component with current filter values
  const updateFilters = () => {
    const filters: FilterValues = {
      selectedSport,
      selectedLeague,
      minOdds,
      maxOdds,
      eventsNumber,
    };
    onFiltersChange(filters);
  };

  const handleSportChange = (value: string) => {
    setSelectedSport(value);
    // Update parent immediately for select changes
    setTimeout(() => updateFilters(), 0);
  };

  const handleLeagueChange = (value: string) => {
    setSelectedLeague(value);
    // Update parent immediately for select changes
    setTimeout(() => updateFilters(), 0);
  };

  const handleMinOddsChange = (value: string) => {
    setMinOdds(value);
  };

  const handleMaxOddsChange = (value: string) => {
    setMaxOdds(value);
  };

  const handleEventsNumberChange = (value: string) => {
    setEventsNumber(value);
  };

  // Handle blur events for text inputs to update parent
  const handleTextInputBlur = () => {
    updateFilters();
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ color: 'text.primary' }}>Sport</InputLabel>
            <Select
              value={selectedSport}
              label="Sport"
              onChange={(e) => handleSportChange(e.target.value)}
              sx={{
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                },
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#000000',
                  borderWidth: '1px',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#000000',
                  borderWidth: '1px',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#000000',
                  borderWidth: '1px',
                },
                '&.Mui-focused .MuiInputLabel-root': {
                  color: 'text.primary',
                },
              }}
            >
              <MenuItem value="football">Football</MenuItem>
              <MenuItem value="basketball">Basketball</MenuItem>
              <MenuItem value="tennis">Tennis</MenuItem>
              <MenuItem value="baseball">Baseball</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel sx={{ color: 'text.primary' }}>League</InputLabel>
            <Select
              value={selectedLeague}
              label="League"
              onChange={(e) => handleLeagueChange(e.target.value)}
              sx={{
                backgroundColor: '#ffffff',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                },
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#000000',
                  borderWidth: '1px',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#000000',
                  borderWidth: '1px',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#000000',
                  borderWidth: '1px',
                },
                '&.Mui-focused .MuiInputLabel-root': {
                  color: 'text.primary',
                },
              }}
            >
              <MenuItem value="premier-league">Premier League</MenuItem>
              <MenuItem value="la-liga">La Liga</MenuItem>
              <MenuItem value="serie-a">Serie A</MenuItem>
              <MenuItem value="bundesliga">Bundesliga</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Events Number"
                type="number"
                value={eventsNumber}
                onChange={(e) => handleEventsNumberChange(e.target.value)}
                onBlur={handleTextInputBlur}
                inputProps={{ min: 1, step: 1 }}
                sx={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: '#000000',
                    },
                    '&:hover fieldset': {
                      borderColor: '#000000',
                    },
                  '&.Mui-focused fieldset': {
                    borderColor: '#000000',
                    borderWidth: '1px',
                  },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'text.primary',
                  },
                  '& .MuiInputLabel-root.Mui-focused': {
                    color: 'text.primary',
                  },
                }}
              />
            </Grid>
        <Grid item xs={12} sm={12} md={6}>
          <Button
            variant="outlined"
            size="small"
            onClick={() => setShowMoreFilters(!showMoreFilters)}
            endIcon={showMoreFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            sx={{
              backgroundColor: '#ffffff',
              border: '1px solid #000000',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              color: 'text.primary',
              fontWeight: 600,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                borderColor: '#000000',
                color: 'text.primary',
              }
            }}
          >
            More filters
          </Button>
        </Grid>
      </Grid>
      
      {/* More Filters Collapse */}
      <Collapse in={showMoreFilters} timeout="auto" unmountOnExit>
        <Box sx={{ mt: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Min Odds"
                type="number"
                value={minOdds}
                onChange={(e) => handleMinOddsChange(e.target.value)}
                onBlur={handleTextInputBlur}
                inputProps={{ min: 1, step: 0.1 }}
                sx={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: '#000000',
                    },
                    '&:hover fieldset': {
                      borderColor: '#000000',
                    },
                  '&.Mui-focused fieldset': {
                    borderColor: '#000000',
                    borderWidth: '1px',
                  },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'text.primary',
                  },
                  '& .MuiInputLabel-root.Mui-focused': {
                    color: 'text.primary',
                  },
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Max Odds"
                type="number"
                value={maxOdds}
                onChange={(e) => handleMaxOddsChange(e.target.value)}
                onBlur={handleTextInputBlur}
                inputProps={{ min: 1, step: 0.1 }}
                sx={{
                  backgroundColor: '#ffffff',
                  borderRadius: '8px',
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: '#000000',
                    },
                    '&:hover fieldset': {
                      borderColor: '#000000',
                    },
                  '&.Mui-focused fieldset': {
                    borderColor: '#000000',
                    borderWidth: '1px',
                  },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'text.primary',
                  },
                  '& .MuiInputLabel-root.Mui-focused': {
                    color: 'text.primary',
                  },
                }}
              />
            </Grid>
          </Grid>
        </Box>
      </Collapse>
    </Box>
  );
};

export default Filters;
