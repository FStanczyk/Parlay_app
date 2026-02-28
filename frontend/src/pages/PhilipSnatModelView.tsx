import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/philip-snat-model-view.scss';
import { apiGet } from '../utils/api';

interface CsvRow {
  [key: string]: string;
}

interface CsvDataResponse {
  success: boolean;
  data: CsvRow[];
  headers: string[];
  file_id: string;
  file_name: string;
  sport: string | null;
  date: string | null;
  row_count: number;
}

const PhilipSnatModelView: React.FC = () => {
  const { file_id } = useParams<{ file_id: string }>();
  const navigate = useNavigate();
  const [csvData, setCsvData] = useState<CsvRow[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [fileName, setFileName] = useState<string>('');
  const [sport, setSport] = useState<string>('');
  const [date, setDate] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCsvData = async () => {
      if (!file_id) {
        setError('File ID is required');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const response = await apiGet<CsvDataResponse>(
          `/philip-snat/prediction-files/${file_id}/data`,
          false
        );

        if (response.success && response.data.length > 0) {
          setCsvData(response.data);
          setFileName(response.file_name);
          setSport(response.sport || '');
          setDate(response.date || '');
          setHeaders(response.headers);
        } else {
          setError('No data available');
        }
      } catch (err) {
        console.error('Failed to fetch CSV data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load CSV data');
      } finally {
        setLoading(false);
      }
    };

    fetchCsvData();
  }, [file_id]);

  const handleBack = () => {
    navigate('/philip-snat-models');
  };

  const NON_PERCENT_COLUMNS = new Set(['date', 'home', 'away']);

  const formatCellValue = (header: string, value: string): string => {
    if (!value || NON_PERCENT_COLUMNS.has(header)) return value || '';
    const num = parseFloat(value);
    if (isNaN(num)) return value;
    return `${(num * 100).toFixed(2)}%`;
  };

  const getCellPercent = (header: string, value: string): number | null => {
    if (!value || NON_PERCENT_COLUMNS.has(header)) return null;
    const num = parseFloat(value);
    return isNaN(num) ? null : num;
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="philip-snat-model-view">
        <div className="philip-snat-model-view__container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="philip-snat-model-view">
        <div className="philip-snat-model-view__container">
          <div className="philip-snat-model-view__error">{error}</div>
          <button
            className="button_primary philip-snat-model-view__back-button"
            onClick={handleBack}
          >
            Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="philip-snat-model-view">
      <div className="philip-snat-model-view__container">
        <div className="philip-snat-model-view__header">
          <div className="philip-snat-model-view__header-info">
            <h2 className="philip-snat-model-view__subtitle">{fileName}</h2>
            {sport && <h1 className="philip-snat-model-view__title">{sport}</h1>}
            {date && <h1 className="philip-snat-model-view__title">{formatDate(date)}</h1>}
          </div>
          <button
            className="button_primary philip-snat-model-view__back-button"
            onClick={handleBack}
          >
            Back
          </button>
        </div>

        {csvData.length > 0 && (
          <div className="philip-snat-model-view__table-wrapper">
            <table className="philip-snat-model-view__table">
              <thead>
                <tr>
                  {headers.map((header) => (
                    <th key={header} className="philip-snat-model-view__th">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {csvData.map((row, index) => (
                  <tr key={index} className="philip-snat-model-view__tr">
                    {headers.map((header) => (
                      <td
                        key={header}
                        className={`philip-snat-model-view__td${header === 'home' || header === 'away' ? ' philip-snat-model-view__td--team' : ''}${getCellPercent(header, row[header]) !== null ? ' philip-snat-model-view__td--percent' : ''}`}
                        style={getCellPercent(header, row[header]) !== null ? { '--cell-pct': `${((getCellPercent(header, row[header]) ?? 0) * 100).toFixed(2)}%` } as React.CSSProperties : undefined}
                      >
                        {formatCellValue(header, row[header])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default PhilipSnatModelView;
