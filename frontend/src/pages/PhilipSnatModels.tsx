import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CsvRecordRow, { CsvRecord } from '../components/CsvRecordRow';
import { apiGet, downloadFile } from '../utils/api';

const PhilipSnatModels: React.FC = () => {
  const navigate = useNavigate();
  const [csvRecords, setCsvRecords] = useState<CsvRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const files = await apiGet<Array<{
          id: string;
          name: string;
          date: string | null;
          sport: string;
        }>>('/philip-snat/prediction-files', false);

        const records: CsvRecord[] = files.map(file => ({
          id: file.id,
          fileName: file.name,
          sport: file.sport,
          date: file.date || '',
          storedFilename: file.name,
        }));

        setCsvRecords(records);
      } catch (err) {
        console.error('Failed to fetch files:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, []);

  const handleView = (record: CsvRecord) => {
    navigate(`/philip-snat-models/${record.id}`);
  };

  const handleDownload = async (record: CsvRecord) => {
    try {
      await downloadFile(
        `/philip-snat/prediction-files/${record.id}/download`,
        record.fileName,
        false
      );
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="philip-snat-models">
        <div className="philip-snat-models__container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="philip-snat-models">
      <div className="philip-snat-models__container">
        <h1 className="philip-snat-models__title">Philip Snat Models</h1>

        {csvRecords.length > 0 ? (
          <div className="philip-snat-models__records">
            <div className="add-ai-predictions__records-list">
              {csvRecords.map((record) => (
                <CsvRecordRow
                  key={record.id}
                  record={record}
                  showDownload={true}
                  showView={true}
                  onView={handleView}
                  onDownload={handleDownload}
                />
              ))}
            </div>
          </div>
        ) : (
          <p className="philip-snat-models__empty">No CSV files available</p>
        )}
      </div>
    </div>
  );
};

export default PhilipSnatModels;
