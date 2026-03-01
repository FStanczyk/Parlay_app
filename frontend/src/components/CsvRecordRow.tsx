import React from 'react';
import { apiDelete, downloadFile } from '../utils/api';

export interface CsvRecord {
  id: string;
  fileName: string;
  sport: string;
  date: string;
  storedFilename?: string;
}

interface CsvRecordRowProps {
  record: CsvRecord;
  showDownload?: boolean;
  showRemove?: boolean;
  showView?: boolean;
  onRemove?: (record: CsvRecord) => void;
  onView?: (record: CsvRecord) => void;
  onDownload?: (record: CsvRecord) => void;
}

const CsvRecordRow: React.FC<CsvRecordRowProps> = ({
  record,
  showDownload = false,
  showRemove = false,
  showView = false,
  onRemove,
  onView,
  onDownload,
}) => {
  const handleDownload = async () => {
    if (onDownload) {
      onDownload(record);
      return;
    }
    if (!record.storedFilename) return;
    try {
      const endpoint = showRemove ? `/admin/uploads/${record.storedFilename}` : `/uploads/${record.storedFilename}`;
      await downloadFile(endpoint, record.fileName);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleRemove = async () => {
    if (!onRemove) return;
    if (!window.confirm(`Are you sure you want to delete "${record.fileName}"?`)) {
      return;
    }
    try {
      await apiDelete(`/admin/philip-snat/prediction-files/${record.id}`);
      onRemove(record);
    } catch (err) {
      console.error('Delete failed:', err);
      alert('Failed to delete file. Please try again.');
    }
  };

  const handleView = () => {
    if (onView) {
      onView(record);
    }
  };

  return (
    <div className="add-ai-predictions__record">
      <span className="add-ai-predictions__record-value">{record.fileName}</span>
      <span className="add-ai-predictions__record-value">{record.sport}</span>
      <span className="add-ai-predictions__record-value">{record.date}</span>
      {record.storedFilename && (showDownload || showRemove || showView) && (
        <div className="add-ai-predictions__record-actions">
          {showDownload && (
            <button
              type="button"
              className="button_primary add-ai-predictions__download-button"
              onClick={handleDownload}
            >
              Download
            </button>
          )}
          {showView && (
            <button
              type="button"
              className="button_primary add-ai-predictions__view-button"
              onClick={handleView}
            >
              View
            </button>
          )}
          {showRemove && (
            <button
              type="button"
              className="button_secondary add-ai-predictions__remove-button"
              onClick={handleRemove}
            >
              Remove
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default CsvRecordRow;
