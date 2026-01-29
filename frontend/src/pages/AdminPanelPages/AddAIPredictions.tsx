import React, { useEffect, useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import CsvRecordRow, { CsvRecord } from '../../components/CsvRecordRow';
import Modal from '../../components/Modal';
import { apiGet, apiPostFile } from '../../utils/api';

interface Sport {
  id: number;
  name: string;
  sport: string;
}

const AddAIPredictions: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedSportId, setSelectedSportId] = useState<number | ''>('');
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [csvRecords, setCsvRecords] = useState<CsvRecord[]>([]);
  const [sports, setSports] = useState<Sport[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSports = async () => {
      try {
        const data = await apiGet<Sport[]>('/philip-snat/sports');
        setSports(data);
      } catch (err) {
        console.error('Failed to fetch sports:', err);
      }
    };
    fetchSports();
  }, []);

  const fetchFiles = async () => {
    try {
      const files = await apiGet<Array<{
        id: number;
        name: string;
        date: string;
        sport: { name: string };
        path: string;
      }>>('/philip-snat/prediction-files');

      const records: CsvRecord[] = files.map(file => ({
        id: file.id.toString(),
        fileName: file.name,
        sport: file.sport?.name || '',
        date: file.date,
        storedFilename: file.path.split('/').pop() || '',
      }));

      setCsvRecords(records);
    } catch (err) {
      console.error('Failed to fetch files:', err);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleAdd = async () => {
    if (!selectedFile || !selectedSportId) {
      setError('Please select a file and sport');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('sport_id', selectedSportId.toString());
      formData.append('date', selectedDate.toISOString().split('T')[0]);

      const response = await apiPostFile<{
        success: boolean;
        data: any[];
        id: number;
        stored_filename: string;
        sport_id: number;
        date: string;
        row_count: number;
      }>(
        '/admin/parse-csv',
        formData
      );

      if (response.success) {
        setIsModalOpen(false);
        setSelectedFile(null);
        setSelectedSportId('');
        setSelectedDate(new Date());
        await fetchFiles();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse CSV');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
    setSelectedSportId('');
    setSelectedDate(new Date());
  };

  return (
    <div className="add-ai-predictions">
      <div className="add-ai-predictions__container">
        <h1>Add AI predictions</h1>
        <button
          className="button_primary add-ai-predictions__button"
          onClick={() => setIsModalOpen(true)}
        >
          Add CSV predictions
        </button>

        {csvRecords.length > 0 && (
          <div className="add-ai-predictions__records">
            <h2 className="add-ai-predictions__records-title">CSV Records</h2>
            <div className="add-ai-predictions__records-list">
              {csvRecords.map((record) => (
                <CsvRecordRow
                  key={record.id}
                  record={record}
                  showDownload={true}
                  showRemove={true}
                  onRemove={async () => {
                    await fetchFiles();
                  }}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCancel}
        title="Add CSV predictions"
        size="medium"
      >
        <div className="add-csv-predictions">
          <div className="add-csv-predictions__field">
            <label htmlFor="csv-file" className="add-csv-predictions__label">
              Choose file
            </label>
            <input
              id="csv-file"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="add-csv-predictions__file-input"
            />
            {selectedFile && (
              <p className="add-csv-predictions__file-name">{selectedFile.name}</p>
            )}
          </div>

          <div className="add-csv-predictions__field">
            <label htmlFor="sport-select" className="add-csv-predictions__label">
              Sport
            </label>
            <select
              id="sport-select"
              className="add-csv-predictions__select"
              value={selectedSportId}
              onChange={(e) => setSelectedSportId(e.target.value ? parseInt(e.target.value) : '')}
            >
              <option value="">Select sport</option>
              {sports.map((sport) => (
                <option key={sport.id} value={sport.id}>
                  {sport.name}
                </option>
              ))}
            </select>
          </div>

          <div className="add-csv-predictions__field">
            <label htmlFor="date-picker" className="add-csv-predictions__label">
              Date
            </label>
            <DatePicker
              id="date-picker"
              selected={selectedDate}
              onChange={(date: Date | null) => setSelectedDate(date || new Date())}
              dateFormat="yyyy-MM-dd"
              className="add-csv-predictions__datepicker"
              wrapperClassName="add-csv-predictions__datepicker-wrapper"
            />
          </div>

          {error && (
            <div className="add-csv-predictions__error">
              {error}
            </div>
          )}

          <div className="add-csv-predictions__actions">
            <button
              type="button"
              className="button_primary add-csv-predictions__button"
              onClick={handleAdd}
              disabled={loading || !selectedFile || !selectedSportId}
            >
              {loading ? 'Processing...' : 'Add'}
            </button>
            <button
              type="button"
              className="button_secondary add-csv-predictions__button"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AddAIPredictions;
