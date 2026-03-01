import React, { useEffect, useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { useTranslation } from '../contexts/TranslationContext';
import { useAuth } from '../contexts/AuthContext';
import { League, leaguesApi, Sport, sportsApi } from '../services/sportsLeaguesService';

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
  onClear: () => void;
  isDemo?: boolean;
}

const Filters: React.FC<FiltersProps> = ({ onFiltersChange, onClear, isDemo = false }) => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const [selectedSport, setSelectedSport] = useState<string>('');
  const [selectedLeague, setSelectedLeague] = useState<string>('');
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
    pushFilters();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSport, selectedLeague, fromDate, toDate]);

  const pushFilters = () => {
    onFiltersChange({
      selectedSport,
      selectedLeague,
      minOdds,
      maxOdds,
      eventsNumber,
      fromDate: fromDate ? fromDate.toISOString().split('T')[0] : '',
      toDate: toDate ? toDate.toISOString().split('T')[0] : '',
    });
  };

  const handleClear = () => {
    setSelectedSport('');
    setSelectedLeague('');
    setMinOdds('');
    setMaxOdds('');
    setEventsNumber('');
    setFromDate(null);
    setToDate(null);
    onClear();
  };

  return (
    <>
      <div className="generator__market-card">
        <div className="generator__market-field">
          <label className="generator__field-label" htmlFor="sport-select">{t.filters.sport}</label>
          <select
            id="sport-select"
            className="filters__select"
            value={selectedSport}
            onChange={(e) => setSelectedSport(e.target.value)}
            disabled={loadingSports}
          >
            <option value="">{t.filters.selectSport}</option>
            {loadingSports ? (
              <option disabled>{t.filters.loadingSports}</option>
            ) : (
              sports.map((sport) => (
                <option key={sport.id} value={sport.id.toString()}>{sport.name}</option>
              ))
            )}
          </select>
        </div>

        <div className="generator__market-field">
          <label className="generator__field-label" htmlFor="league-select">{t.filters.league}</label>
          <select
            id="league-select"
            className="filters__select"
            value={selectedLeague}
            onChange={(e) => setSelectedLeague(e.target.value)}
            disabled={!selectedSport || loadingLeagues}
          >
            <option value="">{t.filters.selectLeague}</option>
            {loadingLeagues ? (
              <option disabled>{t.filters.loadingLeagues}</option>
            ) : leagues.length === 0 ? (
              <option disabled>{selectedSport ? t.filters.noLeaguesAvailable : t.filters.selectSportFirst}</option>
            ) : (
              leagues.map((league) => (
                <option key={league.id} value={league.id.toString()}>{league.name}</option>
              ))
            )}
          </select>
        </div>
      </div>

      {!isDemo && (
        <div className="generator__options-row">
          <div className="generator__option-field">
            <label className="generator__field-label" htmlFor="events-number">{t.filters.eventsNumber}</label>
            <input
              id="events-number"
              className="filters__input"
              type="number"
              min="1"
              max={isAuthenticated ? "50" : "10"}
              step="1"
              value={eventsNumber}
              onChange={(e) => setEventsNumber(e.target.value)}
              onBlur={pushFilters}
            />
          </div>

          <div className="generator__option-field">
            <label className="generator__field-label" htmlFor="min-odds">{t.filters.minOdds}</label>
            <input
              id="min-odds"
              className="filters__input"
              type="number"
              min="1"
              step="0.1"
              value={minOdds}
              onChange={(e) => setMinOdds(e.target.value)}
              onBlur={pushFilters}
            />
          </div>

          <div className="generator__option-field">
            <label className="generator__field-label" htmlFor="max-odds">{t.filters.maxOdds}</label>
            <input
              id="max-odds"
              className="filters__input"
              type="number"
              min="1"
              step="0.1"
              value={maxOdds}
              onChange={(e) => setMaxOdds(e.target.value)}
              onBlur={pushFilters}
            />
          </div>

          <div className="generator__option-field">
            <label className="generator__field-label" htmlFor="from-date">{t.filters.fromDate}</label>
            <DatePicker
              id="from-date"
              selected={fromDate}
              onChange={(date: Date | null) => setFromDate(date)}
              dateFormat="yyyy-MM-dd"
              className="filters__datepicker"
              wrapperClassName="filters__datepicker-wrapper"
            />
          </div>

          <div className="generator__option-field">
            <label className="generator__field-label" htmlFor="to-date">{t.filters.toDate}</label>
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
      )}

      <div className="generator__clear-row">
        <button className="generator__clear-btn" onClick={handleClear}>
          {t.filters.clearFilters}
        </button>
      </div>
    </>
  );
};

export default Filters;
