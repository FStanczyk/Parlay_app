import React, { useState, useEffect } from 'react';
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
  CircularProgress,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { sportsApi, leaguesApi, Sport, League } from '../services/sportsLeaguesService';

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
  
  // Data states
  const [sports, setSports] = useState<Sport[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [loadingSports, setLoadingSports] = useState(true);
  const [loadingLeagues, setLoadingLeagues] = useState(false);

  // Fetch sports on component mount
  useEffect(() => {
    const fetchSports = async () => {
      try {
        setLoadingSports(true);
        const sportsData = await sportsApi.getAll();
        setSports(sportsData);
      } catch (error) {
        console.error('Error fetching sports:', error);
      } finally {
        setLoadingSports(false);
      }
    };

    fetchSports();
  }, []);

  // Fetch leagues when sport changes
  useEffect(() => {
    const fetchLeagues = async () => {
      if (selectedSport) {
        try {
          setLoadingLeagues(true);
          const sportId = parseInt(selectedSport);
          const leaguesData = await leaguesApi.getAll(sportId);
          setLeagues(leaguesData);
          // Reset selected league when sport changes
          setSelectedLeague('');
        } catch (error) {
          console.error('Error fetching leagues:', error);
        } finally {
          setLoadingLeagues(false);
        }
      } else {
        setLeagues([]);
        setSelectedLeague('');
      }
    };

    fetchLeagues();
  }, [selectedSport]);

  // Update parent when sport or league changes
  useEffect(() => {
    updateFilters();
  }, [selectedSport, selectedLeague]);

  // Function to update parent component with current filter values
  const updateFilters = () => {
    const filters: FilterValues = {
      selectedSport,
      selectedLeague,
      minOdds,
      maxOdds,
      eventsNumber,
    };
    console.log('Filters component sending to parent:', filters);
    onFiltersChange(filters);
  };

  const handleSportChange = (value: string) => {
    setSelectedSport(value);
    // Clear league selection when sport changes
    setSelectedLeague('');
  };

  const handleLeagueChange = (value: string) => {
    console.log('League changed to:', value);
    setSelectedLeague(value);
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

  // Clear all filters
  const handleClearFilters = () => {
    setSelectedSport('');
    setSelectedLeague('');
    setMinOdds('');
    setMaxOdds('');
    setEventsNumber('');
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
              disabled={loadingSports}
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
              {loadingSports ? (
                <MenuItem disabled>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={16} />
                    Loading sports...
                  </Box>
                </MenuItem>
              ) : (
                sports.map((sport) => (
                  <MenuItem key={sport.id} value={sport.id.toString()}>
                    {sport.name}
                  </MenuItem>
                ))
              )}
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
              disabled={!selectedSport || loadingLeagues}
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
              {loadingLeagues ? (
                <MenuItem disabled>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={16} />
                    Loading leagues...
                  </Box>
                </MenuItem>
              ) : leagues.length === 0 ? (
                <MenuItem disabled>
                  {selectedSport ? 'No leagues available' : 'Select a sport first'}
                </MenuItem>
              ) : (
                leagues.map((league) => (
                  <MenuItem key={league.id} value={league.id.toString()}>
                    {league.name}
                  </MenuItem>
                ))
              )}
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
        <Grid item xs={12} sm={6} md={3}>
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
          <Button
            variant="outlined"
            size="small"
            onClick={handleClearFilters}
            sx={{
              backgroundColor: '#ffffff',
              border: '1px solid #000000',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              color: 'text.primary',
              marginLeft: '10px',
              fontWeight: 600,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                borderColor: '#000000',
                color: 'text.primary',
              }
            }}
          >
            Clear filters
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
