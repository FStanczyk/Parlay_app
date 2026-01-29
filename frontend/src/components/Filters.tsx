import React, { useEffect, useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { FiChevronDown, FiChevronUp } from 'react-icons/fi';
import { useTranslation } from '../contexts/TranslationContext';
import { useAuth } from '../contexts/AuthContext';
import { League, leaguesApi, Sport, sportsApi } from '../services/sportsLeaguesService';
import { Icon } from '../utils/Icon';

export interface FilterValues {
  selectedSport: string;
  selectedLeague: string;
  minOdds: string;
  maxOdds: string;
  eventsNumber: string;
  fromDate: string;
  toDate: string;
}

interface FiltersProps {
  onFiltersChange: (filters: FilterValues) => void;
  isDemo?: boolean;
}

const Filters: React.FC<FiltersProps> = ({ onFiltersChange, isDemo = false }) => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const [selectedSport, setSelectedSport] = useState<string>('');
  const [selectedLeague, setSelectedLeague] = useState<string>('');
  const [showMoreFilters, setShowMoreFilters] = useState(false);
  const [minOdds, setMinOdds] = useState<string>('');
  const [maxOdds, setMaxOdds] = useState<string>('');
  const [eventsNumber, setEventsNumber] = useState<string>('');
  const [fromDate, setFromDate] = useState<Date | null>(null);
  const [toDate, setToDate] = useState<Date | null>(null);

  const [sports, setSports] = useState<Sport[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [loadingSports, setLoadingSports] = useState(true);
  const [loadingLeagues, setLoadingLeagues] = useState(false);

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

  useEffect(() => {
    const fetchLeagues = async () => {
      if (selectedSport) {
        try {
          setLoadingLeagues(true);
          const sportId = parseInt(selectedSport);
          const leaguesData = await leaguesApi.getAll(sportId);
          setLeagues(leaguesData);
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

  useEffect(() => {
    updateFilters();
  }, [selectedSport, selectedLeague, fromDate, toDate]);

  const updateFilters = () => {
    const filters: FilterValues = {
      selectedSport,
      selectedLeague,
      minOdds,
      maxOdds,
      eventsNumber,
      fromDate: fromDate ? fromDate.toISOString().split('T')[0] : '',
      toDate: toDate ? toDate.toISOString().split('T')[0] : '',
    };
    console.log('Filters component sending to parent:', filters);
    onFiltersChange(filters);
  };

  const handleSportChange = (value: string) => {
    setSelectedSport(value);
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

  const handleTextInputBlur = () => {
    updateFilters();
  };

  const handleClearFilters = () => {
    setSelectedSport('');
    setSelectedLeague('');
    setMinOdds('');
    setMaxOdds('');
    setEventsNumber('');
    setFromDate(null);
    setToDate(null);
  };

  return (
    <div className="filters">
      <h3 className="filters__label italic-title">{t.filters.filters}</h3>
      <div className="filters__grid">
        <div className="filters__market-selection">
            <h4 className="filters__label italic-title">{t.filters.marketSelection}</h4>
            <div className="filters__market-selection-content">
              <div className="filters__field">
              <label htmlFor="sport-select" className="filters__label">{t.filters.sport}</label>
              <select
                id="sport-select"
                className="filters__select"
                value={selectedSport}
                onChange={(e) => handleSportChange(e.target.value)}
                disabled={loadingSports}
              >
                <option value="">{t.filters.selectSport}</option>
                {loadingSports ? (
                  <option disabled>{t.filters.loadingSports}</option>
                ) : (
                  sports.map((sport) => (
                    <option key={sport.id} value={sport.id.toString()}>
                      {sport.name}
                    </option>
                  ))
                )}
              </select>
            </div>

            <div className="filters__field">
              <label htmlFor="league-select" className="filters__label">{t.filters.league}</label>
              <select
                id="league-select"
                className="filters__select"
                value={selectedLeague}
                onChange={(e) => handleLeagueChange(e.target.value)}
                disabled={!selectedSport || loadingLeagues}
              >
                <option value="">{t.filters.selectLeague}</option>
                {loadingLeagues ? (
                  <option disabled>{t.filters.loadingLeagues}</option>
                ) : leagues.length === 0 ? (
                  <option disabled>
                    {selectedSport ? t.filters.noLeaguesAvailable : t.filters.selectSportFirst}
                  </option>
                ) : (
                  leagues.map((league) => (
                    <option key={league.id} value={league.id.toString()}>
                      {league.name}
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>
        </div>

        {!isDemo && (
          <div className="filters__field">
            <label htmlFor="events-number" className="filters__label">{t.filters.eventsNumber}</label>
            <input
              id="events-number"
              className="filters__input"
              type="number"
              min="1"
              max={isAuthenticated ? "50" : "10"}
              step="1"
              value={eventsNumber}
              onChange={(e) => handleEventsNumberChange(e.target.value)}
              onBlur={handleTextInputBlur}
            />
          </div>
        )}

        <div className="filters__field filters__field--actions">
          {!isDemo && (
            <button
              className="filters__button button_primary"
              onClick={() => setShowMoreFilters(!showMoreFilters)}
            >
              {t.filters.moreFilters}
              {showMoreFilters ? <Icon component={FiChevronUp} aria-hidden={true} /> : <Icon component={FiChevronDown} aria-hidden={true} />}
            </button>
          )}
          <button
            className="filters__button button_primary"
            onClick={handleClearFilters}
          >
            {t.filters.clearFilters}
          </button>
        </div>
      </div>

      {showMoreFilters && !isDemo && (
        <div className="filters__more">
          <div className="filters__grid">
            <div className="filters__field">
              <label htmlFor="min-odds" className="filters__label">{t.filters.minOdds}</label>
              <input
                id="min-odds"
                className="filters__input"
                type="number"
                min="1"
                step="0.1"
                value={minOdds}
                onChange={(e) => handleMinOddsChange(e.target.value)}
                onBlur={handleTextInputBlur}
              />
            </div>

            <div className="filters__field">
              <label htmlFor="max-odds" className="filters__label">{t.filters.maxOdds}</label>
              <input
                id="max-odds"
                className="filters__input"
                type="number"
                min="1"
                step="0.1"
                value={maxOdds}
                onChange={(e) => handleMaxOddsChange(e.target.value)}
                onBlur={handleTextInputBlur}
              />
            </div>

            <div className="filters__field">
              <label htmlFor="from-date" className="filters__label">{t.filters.fromDate}</label>
              <DatePicker
                id="from-date"
                selected={fromDate}
                onChange={(date: Date | null) => setFromDate(date)}
                dateFormat="yyyy-MM-dd"
                className="filters__datepicker"
                wrapperClassName="filters__datepicker-wrapper"
              />
            </div>

            <div className="filters__field">
              <label htmlFor="to-date" className="filters__label">{t.filters.toDate}</label>
              <DatePicker
                id="to-date"
                selected={toDate}
                onChange={(date: Date | null) => setToDate(date)}
                dateFormat="yyyy-MM-dd"
                minDate={fromDate || undefined}
                className="filters__datepicker"
                wrapperClassName="filters__datepicker-wrapper"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Filters;
